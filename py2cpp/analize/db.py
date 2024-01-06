from dataclasses import dataclass, field
from typing import NamedTuple, TypeAlias

from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
from py2cpp.lang.implementation import injectable
from py2cpp.module.modules import Module, Modules
import py2cpp.node.definition as defs

DeclVar: TypeAlias = defs.Parameter | defs.AnnoAssign | defs.MoveAssign
DeclAll: TypeAlias = defs.Parameter | defs.AnnoAssign | defs.MoveAssign | defs.ClassKind


class SymbolRow(NamedTuple):
	"""シンボルデータ

	Attributes:
		ref_path (str): 参照パス
		org_path (str): 参照パス(オリジナル)
		module (Module): 展開先のモジュール
		symbol (Symbol): シンボルノード
		types (ClassKind): タイプノード
		decl (DeclAll): 宣言ノード
	"""
	ref_path: str
	org_path: str
	module: Module
	symbol: defs.Symbol
	types: defs.ClassKind
	decl: DeclAll

	def to(self, module: Module) -> 'SymbolRow':
		"""展開先を変更したインスタンスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			SymbolRow: インスタンス
		"""
		return SymbolRow(self.path_to(module), self.org_path, module, self.symbol, self.types, self.decl)

	def path_to(self, module: Module) -> str:
		"""展開先を変更した参照パスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			str: 展開先の参照パス
		"""
		return self.ref_path.replace(self.module.path, module.path)

	def varnize(self, var: DeclVar) -> 'SymbolRow':
		"""変数シンボル用のデータに変換

		Args:
			var (DeclVar): 変数宣言ノード
		Returns:
			SymbolRow: インスタンス
		"""
		return SymbolRow(self.ref_path, self.org_path, self.module, self.symbol, self.types, var)


@dataclass
class Expanded:
	"""展開時のテンポラリーデータ

	Attributes:
		rows (SymbolDB): シンボルテーブル
		decl_vars (list[DeclVar]): 変数リスト
		import_nodes (list[Import]): インポートリスト
	"""
	rows: dict[str, SymbolRow] = field(default_factory=dict)
	decl_vars: list[DeclVar] = field(default_factory=list)
	import_nodes: list[defs.Import] = field(default_factory=list)


class SymbolDB:
	"""シンボルテーブル"""

	@injectable
	def __init__(self, modules: Modules) -> None:
		"""インスタンスを生成

		Args:
			modules (Modules): モジュールマネージャー @inject
		"""
		self.rows = self.__make_rows(modules)

	def __make_rows(self, modules: Modules) -> dict[str, SymbolRow]:
		"""シンボルテーブルを生成

		Args:
			modules (Modules): モジュールマネージャー
		Returns:
			dict[str, SymbolRow]: シンボルテーブル
		"""
		main = modules.main

		# メインモジュールを展開
		expends: dict[Module, Expanded] = {}
		expends[main] = self.__expand_module(main)

		# インポートモジュールを全て展開
		import_index = 0
		import_modules_from_main = [modules.load(node.module_path.tokens) for node in expends[main].import_nodes]
		import_modules = [*modules.libralies, *import_modules_from_main]
		while import_index < len(import_modules):
			import_module = import_modules[import_index]
			expanded = self.__expand_module(import_module)
			import_modules_from_depended = [modules.load(node.module_path.tokens) for node in expanded.import_nodes]
			import_modules = [*import_modules, *import_modules_from_depended]
			expends[import_module] = expanded
			import_index += 1

		all_modules = [*import_modules, main]
		for expand_module in all_modules:
			expand_target = expends[expand_module]

			# 標準ライブラリを展開
			if expand_module not in modules.libralies:
				for core_module in modules.libralies:
					# 第1層で宣言されているシンボルに限定
					entrypoint = core_module.entrypoint.as_a(defs.Entrypoint)
					primary_symbol_names = [node.symbol.tokens for node in entrypoint.statements if isinstance(node, DeclAll)]
					expanded = expends[core_module]
					filtered_db = {row.path_to(expand_module): row.to(expand_module) for row in expanded.rows.values() if row.symbol.tokens in primary_symbol_names}
					expand_target.rows = {**filtered_db, **expand_target.rows}

			# インポートモジュールを展開
			# XXX 別枠として分離するより、ステートメントの中で処理するのが理想
			# XXX また、ステートメントのスコープも合わせて考慮
			for import_node in expand_target.import_nodes:
				# import句で明示されたシンボルに限定
				imported_symbol_names = [symbol.tokens for symbol in import_node.import_symbols]
				import_module = modules.load(import_node.module_path.tokens)
				expanded = expends[import_module]
				filtered_db = {row.path_to(expand_module): row.to(expand_module) for row in expanded.rows.values() if row.symbol.tokens in imported_symbol_names}
				expand_target.rows = {**filtered_db, **expand_target.rows}

			# 展開対象モジュールの変数シンボルを展開
			for var in expand_target.decl_vars:
				expand_target.rows[var.symbol.domain_id] = self.__resolve_var_type(var, expand_target.rows).varnize(var)

		# シンボルテーブルを統合
		rows: dict[str, SymbolRow] = {}
		for expanded in expends.values():
			rows = {**expanded.rows, **rows}

		return rows

	def __expand_module(self, module: Module) -> Expanded:
		"""モジュールの全シンボルを展開

		Args:
			module (Module): モジュール
		Returns:
			Expanded: 展開データ
		"""
		rows: dict[str, SymbolRow] = {}
		decl_vars: list[DeclVar] = []
		import_nodes: list[defs.Import] = []
		entrypoint = module.entrypoint.as_a(defs.Entrypoint)
		for node in entrypoint.flatten():
			if isinstance(node, defs.ClassKind):
				rows[node.domain_id] = SymbolRow(node.domain_id, node.domain_id, module, node.symbol, node, node)

			if type(node) is defs.Import:
				import_nodes.append(node)

			if type(node) is defs.Function:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.ClassMethod:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Constructor:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Method:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Class:
				decl_vars.extend(node.vars)
			elif type(node) is defs.Enum:
				decl_vars.extend(node.vars)

		# XXX calculatedに含まれないためエントリーポイントは個別に処理
		decl_vars = [*entrypoint.decl_vars, *decl_vars]

		return Expanded(rows, decl_vars, import_nodes)

	def __resolve_var_type(self, var: DeclVar, rows: dict[str, SymbolRow]) -> SymbolRow:
		"""シンボルテーブルから変数の型を解決

		Args:
			var (DeclVar): 変数宣言ノード
			rows (dict[str, SymbolRow]): シンボルテーブル
		Returns:
			SymbolRow: シンボルデータ
		"""
		type_symbol = self.__fetch_type_symbol(var)
		candidates = []
		if type_symbol is not None:
			candidates = [type_symbol.domain_id, type_symbol.domain_name]
		else:
			# 型が不明な変数はUnknownにフォールバック
			# XXX Unknownの名前は重要なので定数化などの方法で明示
			candidates = [DSN.join(var.module_path, 'Unknown')]

		for candidate in candidates:
			if candidate in rows:
				return rows[candidate]

		raise LogicError(f'Unresolve var type. symbol: {var.symbol.tokens}')

	def __fetch_type_symbol(self, var: DeclVar) -> defs.Symbol | None:
		"""変数の型のシンボルノードを取得。型が不明な場合はNoneを返却

		Args:
			var (DeclVar): 変数宣言ノード
		Returns:
			Symbol | None: シンボルノード
		"""
		if isinstance(var, (defs.AnnoAssign, defs.Parameter)):
			if var.symbol.is_a(defs.This):
				return var.symbol.as_a(defs.This).class_types.as_a(defs.ClassKind).symbol
			elif var.var_type.is_a(defs.Symbol):
				return var.var_type.as_a(defs.Symbol)
			elif var.var_type.is_a(defs.GenericType):
				return var.var_type.as_a(defs.GenericType).symbol

		return None
