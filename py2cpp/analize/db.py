from dataclasses import dataclass, field
from typing import NamedTuple

from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
from py2cpp.lang.implementation import injectable
from py2cpp.module.modules import Module, Modules
import py2cpp.node.definition as defs


class SymbolRaw(NamedTuple):
	"""シンボルデータ

	Attributes:
		ref_path (str): 参照パス
		org_path (str): 参照パス(オリジナル)
		module (Module): 展開先のモジュール
		symbol (Declable): シンボル宣言ノード
		types (ClassKind): タイプノード
		decl (DeclAll): 宣言ステートメントノード
	"""
	ref_path: str
	org_path: str
	module: Module
	symbol: defs.Declable
	types: defs.ClassKind
	decl: defs.DeclAll

	def to(self, module: Module) -> 'SymbolRaw':
		"""展開先を変更したインスタンスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.path_to(module), self.org_path, module, self.symbol, self.types, self.decl)

	def path_to(self, module: Module) -> str:
		"""展開先を変更した参照パスを生成

		Args:
			module (Module): 展開先のモジュール
		Returns:
			str: 展開先の参照パス
		"""
		return self.ref_path.replace(self.module.path, module.path)

	def varnize(self, var: defs.DeclVars) -> 'SymbolRaw':
		"""変数シンボル用のデータに変換

		Args:
			var (DeclVars): 変数宣言ノード
		Returns:
			SymbolRaw: インスタンス
		"""
		return SymbolRaw(self.ref_path, self.org_path, self.module, self.symbol, self.types, var)


@dataclass
class Expanded:
	"""展開時のテンポラリーデータ

	Attributes:
		raws (SymbolDB): シンボルテーブル
		decl_vars (list[DeclVars]): 変数リスト
		import_nodes (list[Import]): インポートリスト
	"""
	raws: dict[str, SymbolRaw] = field(default_factory=dict)
	decl_vars: list[defs.DeclVars] = field(default_factory=list)
	import_nodes: list[defs.Import] = field(default_factory=list)


class SymbolDB:
	"""シンボルテーブル"""

	@injectable
	def __init__(self, modules: Modules) -> None:
		"""インスタンスを生成

		Args:
			modules (Modules): モジュールマネージャー @inject
		"""
		self.raws = self.__make_raws(modules)

	def __make_raws(self, modules: Modules) -> dict[str, SymbolRaw]:
		"""シンボルテーブルを生成

		Args:
			modules (Modules): モジュールマネージャー
		Returns:
			dict[str, SymbolRaw]: シンボルテーブル
		"""
		main = modules.main

		# メインモジュールを展開
		expends: dict[Module, Expanded] = {}
		expends[main] = self.__expand_module(main)

		# インポートモジュールを全て展開
		import_index = 0
		import_modules_from_main = [modules.load(node.import_path.tokens) for node in expends[main].import_nodes]
		import_modules = [*modules.libralies, *import_modules_from_main]
		while import_index < len(import_modules):
			import_module = import_modules[import_index]
			expanded = self.__expand_module(import_module)
			import_modules_from_depended = [modules.load(node.import_path.tokens) for node in expanded.import_nodes]
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
					primary_symbol_names = [node.symbol.tokens for node in entrypoint.statements if isinstance(node, defs.DeclAll)]
					expanded = expends[core_module]
					filtered_db = {raw.path_to(expand_module): raw.to(expand_module) for raw in expanded.raws.values() if raw.symbol.tokens in primary_symbol_names}
					expand_target.raws = {**filtered_db, **expand_target.raws}

			# インポートモジュールを展開
			# XXX 別枠として分離するより、ステートメントの中で処理するのが理想
			# XXX また、ステートメントのスコープも合わせて考慮
			for import_node in expand_target.import_nodes:
				# import句で明示されたシンボルに限定
				imported_symbol_names = [symbol.tokens for symbol in import_node.import_symbols]
				import_module = modules.load(import_node.import_path.tokens)
				expanded = expends[import_module]
				filtered_db = {raw.path_to(expand_module): raw.to(expand_module) for raw in expanded.raws.values() if raw.symbol.tokens in imported_symbol_names}
				expand_target.raws = {**filtered_db, **expand_target.raws}

			# 展開対象モジュールの変数シンボルを展開
			for var in expand_target.decl_vars:
				expand_target.raws[var.symbol.fullyname] = self.__resolve_var_type(var, expand_target.raws).varnize(var)

		# シンボルテーブルを統合
		raws: dict[str, SymbolRaw] = {}
		for expanded in expends.values():
			raws = {**expanded.raws, **raws}

		return raws

	def __expand_module(self, module: Module) -> Expanded:
		"""モジュールの全シンボルを展開

		Args:
			module (Module): モジュール
		Returns:
			Expanded: 展開データ
		"""
		raws: dict[str, SymbolRaw] = {}
		decl_vars: list[defs.DeclVars] = []
		import_nodes: list[defs.Import] = []
		entrypoint = module.entrypoint.as_a(defs.Entrypoint)
		for node in entrypoint.flatten():
			if isinstance(node, defs.ClassKind):
				raws[node.fullyname] = SymbolRaw(node.fullyname, node.fullyname, module, node.symbol, node, node)

			if type(node) is defs.Import:
				import_nodes.append(node)

			if isinstance(node, defs.Function):
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Class:
				decl_vars.extend(node.class_vars)
				decl_vars.extend(node.this_vars)
			elif type(node) is defs.Enum:
				decl_vars.extend(node.vars)

		# XXX calculatedに含まれないためエントリーポイントは個別に処理
		decl_vars = [*entrypoint.decl_vars, *decl_vars]

		return Expanded(raws, decl_vars, import_nodes)

	def __resolve_var_type(self, var: defs.DeclVars, raws: dict[str, SymbolRaw]) -> SymbolRaw:
		"""シンボルテーブルから変数の型を解決

		Args:
			var (DeclVars): 変数宣言ノード
			raws (dict[str, SymbolRaw]): シンボルテーブル
		Returns:
			SymbolRaw: シンボルデータ
		"""
		domain_type = self.__fetch_domain_type(var)
		if domain_type is not None:
			scopes = [DSN.left(domain_type.scope, DSN.elem_counts(domain_type.scope) - i) for i in range(DSN.elem_counts(domain_type.scope))]
			candidates = [DSN.join(scope, domain_type.domain_name) for scope in scopes]
		else:
			# 型が不明な変数はUnknownにフォールバック
			# XXX Unknownの名前は重要なので定数化などの方法で明示
			candidates = [DSN.join(var.module_path, 'Unknown')]

		for candidate in candidates:
			if candidate in raws:
				return raws[candidate]

		raise LogicError(f'Unresolve var type. var: {var}, domain: {domain_type.fullyname if domain_type is not None else "Unknown"}, candidates: {candidates}')

	def __fetch_domain_type(self, var: defs.DeclVars) -> defs.Type | defs.ClassKind | None:
		"""変数の型のドメインを取得。型が不明な場合はNoneを返却

		Args:
			var (DeclVars): 変数宣言ノード
		Returns:
			Type | ClassKind | None: 型/クラス定義ノード。不明な場合はNone
		"""
		if isinstance(var, (defs.AnnoAssign, defs.Catch)):
			return var.var_type
		elif isinstance(var, defs.Parameter):
			if isinstance(var.symbol, defs.DeclClassParam):
				return var.symbol.class_types.as_a(defs.ClassKind)
			elif isinstance(var.symbol, defs.DeclThisParam):
				return var.symbol.class_types.as_a(defs.ClassKind)
			else:
				return var.var_type.as_a(defs.Type)
		elif isinstance(var, (defs.MoveAssign, defs.For)):
			# 型指定が無いため全てUnknown
			return None

		return None
