from dataclasses import dataclass, field
from typing import NamedTuple, TypeAlias

from py2cpp.ast.dns import domainize
from py2cpp.errors import LogicError
from py2cpp.module.module import Module
from py2cpp.module.modules import Modules
import py2cpp.node.definition as defs


class SymbolRow(NamedTuple):
	"""シンボル情報

	Attributes:
		ref_path: 参照パス
		org_path: 参照パス(オリジナル)
		module: 展開先のモジュール
		symbol: シンボルノード
		types: タイプ(クラス/関数全般)
	"""
	ref_path: str
	org_path: str
	module: Module
	symbol: defs.Symbol
	types: defs.Types

	def to(self, module: Module) -> 'SymbolRow':
		"""展開先を変更したインスタンスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			SymbolRow: インスタンス
		"""
		return SymbolRow(self.path_to(module), self.org_path, module, self.symbol, self.types)

	def path_to(self, module: Module) -> str:
		"""展開先を変更した参照パスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			str: 展開先の参照パス
		"""
		return self.ref_path.replace(self.module.path, module.path)


SymbolDB: TypeAlias = dict[str, SymbolRow]
DeclVar: TypeAlias = defs.Parameter | defs.AnnoAssign | defs.MoveAssign
DeclAll: TypeAlias = defs.Parameter | defs.AnnoAssign | defs.MoveAssign | defs.Types


@dataclass
class Expanded:
	"""展開時のテンポラリーデータ

	Attributes:
		db (SymbolDB): シンボルテーブル
		decl_vars (list[DeclVar]): 変数リスト
		import_nodes (list[Import]): インポートリスト
	"""
	db: SymbolDB = field(default_factory=dict)
	decl_vars: list[DeclVar] = field(default_factory=list)
	import_nodes: list[defs.Import] = field(default_factory=list)


class SymbolDBFactory:
	"""シンボルテーブルファクトリー"""

	@classmethod
	def create(cls, modules: Modules) -> SymbolDB:
		"""シンボルテーブルを生成

		Args:
			modules (Modules): モジュールマネージャー
		Returns:
			SymbolDB: シンボルテーブル
		"""
		main = modules.main

		# メインモジュールを展開
		expends: dict[Module, Expanded] = {}
		expends[main] = cls.__expand_module(main)

		# インポートモジュールを全て展開
		import_index = 0
		import_modules_from_main = [modules.load(node.module_path.tokens) for node in expends[main].import_nodes]
		import_modules = [*modules.core_libralies, *import_modules_from_main]
		while import_index < len(import_modules):
			import_module = import_modules[import_index]
			expanded = cls.__expand_module(import_module)
			import_modules_from_depended = [modules.load(node.module_path.tokens) for node in expanded.import_nodes]
			import_modules = [*import_modules, *import_modules_from_depended]
			expends[import_module] = expanded
			import_index += 1

		all_modules = [*import_modules, main]
		for expand_module in all_modules:
			expand_target = expends[expand_module]

			# 標準ライブラリを展開
			if expand_module not in modules.core_libralies:
				for core_module in modules.core_libralies:
					# 第1層で宣言されているシンボルに限定
					entrypoint = core_module.entrypoint(defs.Entrypoint)
					primary_symbol_names = [node.symbol.tokens for node in entrypoint.statements if isinstance(node, DeclAll)]
					expanded = expends[core_module]
					filtered_db = {row.path_to(expand_module): row.to(expand_module) for row in expanded.db.values() if row.symbol.tokens in primary_symbol_names}
					expand_target.db = {**filtered_db, **expand_target.db}

			# インポートモジュールを展開
			# XXX 別枠として分離するより、ステートメントの中で処理するのが理想
			# XXX また、ステートメントのスコープも合わせて考慮
			for import_node in expand_target.import_nodes:
				# import句で明示されたシンボルに限定
				imported_symbol_names = [symbol.tokens for symbol in import_node.import_symbols]
				import_module = modules.load(import_node.module_path.tokens)
				expanded = expends[import_module]
				filtered_db = {row.path_to(expand_module): row.to(expand_module) for row in expanded.db.values() if row.symbol.tokens in imported_symbol_names}
				expand_target.db = {**filtered_db, **expand_target.db}

			# 展開対象モジュールの変数シンボルを展開
			for var in expand_target.decl_vars:
				# XXX This以外を登録
				if not var.symbol.is_a(defs.This):
					expand_target.db[var.symbol.domain_id] = cls.__resolve_var_type(var, expand_target.db)

		# シンボルテーブルを統合
		db: SymbolDB = {}
		for expanded in expends.values():
			db = {**expanded.db, **db}

		return db

	@classmethod
	def __expand_module(cls, main: Module) -> Expanded:
		"""モジュールの全シンボルを展開

		Args:
			module (Module): モジュール
		Returns:
			Expanded: 展開データ
		"""
		db: SymbolDB = {}
		decl_vars: list[DeclVar] = []
		import_nodes: list[defs.Import] = []
		entrypoint = main.entrypoint(defs.Entrypoint)
		for node in entrypoint.flatten():
			if isinstance(node, defs.Types):
				db[node.domain_id] = SymbolRow(node.domain_id, node.domain_id, node.module, node.symbol, node)

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

		return Expanded(db, decl_vars, import_nodes)

	@classmethod
	def __resolve_var_type(cls, var: DeclVar, db: SymbolDB) -> SymbolRow:
		"""シンボルテーブルから変数の型を解決

		Args:
			var (DeclVar): 変数
			db (SymbolDB): シンボルテーブル
		Returns:
			SymbolRow: シンボル情報
		"""
		type_symbol = cls.__fetch_type_symbol(var)
		candidates = []
		if type_symbol is not None:
			candidates = [type_symbol.domain_id, type_symbol.domain_name]
		else:
			# 型が不明な変数はUnknownにフォールバック
			# XXX Unknownの名前は重要なので定数化などの方法で明示
			candidates = [domainize(var.module.path, 'Unknown')]

		for candidate in candidates:
			if candidate in db:
				return db[candidate]

		raise LogicError(f'Unresolve var type. symbol: {var.symbol.tokens}')

	@classmethod
	def __fetch_type_symbol(cls, var: DeclVar) -> defs.Symbol | None:
		"""変数の型のシンボルノードを取得

		Args:
			var (DeclVar): 変数
		Returns:
			Symbol: シンボルノード
		"""
		if isinstance(var, (defs.AnnoAssign, defs.Parameter)):
			if var.var_type.is_a(defs.Symbol):
				return var.var_type.as_a(defs.Symbol)
			elif var.var_type.is_a(defs.GenericType):
				return var.var_type.as_a(defs.GenericType).symbol

		return None
