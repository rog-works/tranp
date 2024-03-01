from dataclasses import dataclass, field

import rogw.tranp.compatible.python.classes as classes
from rogw.tranp.lang.implementation import injectable
from rogw.tranp.module.modules import Module, Modules
from rogw.tranp.syntax.ast.dsn import DSN
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.semantics.finder import SymbolFinder
from rogw.tranp.semantics.symbol import Symbol, Reflection, SymbolRaws


@dataclass
class Expanded:
	"""展開時のテンポラリーデータ

	Attributes:
		raws (SymbolRaws): シンボルテーブル
		decl_vars (list[DeclVars]): 変数リスト
		import_nodes (list[Import]): インポートリスト
	"""
	raws: SymbolRaws = field(default_factory=SymbolRaws)
	decl_vars: list[defs.DeclVars] = field(default_factory=list)
	import_nodes: list[defs.Import] = field(default_factory=list)


class FromModules:
	"""モジュールからシンボルテーブルの生成
	
	Note:
		プリプロセッサーの最初に実行することが前提
	"""

	@injectable
	def __init__(self, finder: SymbolFinder) -> None:
		"""インスタンスを生成

		Args:
			finder (SymbolFinder): シンボル検索 @inject
		"""
		self.finder = finder

	@injectable
	def __call__(self, modules: Modules, raws: SymbolRaws) -> SymbolRaws:
		"""シンボルテーブルを生成

		Args:
			modules (Modules): モジュールマネージャー @inject
			raws (SymbolRaws): シンボルテーブル
		Returns:
			SymbolRaws: シンボルテーブル
		"""
		main = modules.main

		# メインモジュールを展開
		expands: dict[Module, Expanded] = {}
		expands[main] = self.expand_module(main)

		# インポートモジュールを全て展開
		import_index = 0
		import_modules_from_main = [modules.load(node.import_path.tokens) for node in expands[main].import_nodes]
		import_modules: dict[str, Module] = {**{module.path: module for module in modules.libralies}, **{module.path: module for module in import_modules_from_main}}
		while import_index < len(import_modules):
			import_module = list(import_modules.values())[import_index]
			expanded = self.expand_module(import_module)
			import_modules_from_depended = [modules.load(node.import_path.tokens) for node in expanded.import_nodes]
			import_modules = {**import_modules, **{module.path: module for module in import_modules_from_depended}}
			expands[import_module] = expanded
			import_index += 1

		all_modules = {**import_modules, main.path: main}
		for expand_module in all_modules.values():
			expand_target = expands[expand_module]

			# 標準ライブラリを展開
			core_primary_raws = SymbolRaws()
			if expand_module not in modules.libralies:
				for core_module in modules.libralies:
					# 第1層で宣言されているシンボルに限定
					entrypoint = core_module.entrypoint.as_a(defs.Entrypoint)
					primary_symbol_names = [node.fullyname for node in entrypoint.statements if isinstance(node, defs.DeclAll)]
					expanded = expands[core_module]
					core_primary_raws.merge({fullyname: expanded.raws[fullyname] for fullyname in primary_symbol_names})

			# インポートモジュールを展開
			# XXX 別枠として分離するより、ステートメントの中で処理するのが理想
			# XXX また、ステートメントのスコープも合わせて考慮
			imported_raws = SymbolRaws()
			for import_node in expand_target.import_nodes:
				# import句で明示されたシンボルに限定
				imported_symbol_names = [symbol.tokens for symbol in import_node.import_symbols]
				import_module = modules.load(import_node.import_path.tokens)
				expanded = expands[import_module]
				filtered_raws = [expanded.raws[DSN.join(import_module.path, name)].to.imports(import_node) for name in imported_symbol_names]
				filtered_db = {raw.ref_fullyname: raw for raw in filtered_raws}
				imported_raws.merge(filtered_db)

			# 展開対象モジュールの変数シンボルを展開
			expand_target.raws = SymbolRaws.new(core_primary_raws, imported_raws, expand_target.raws)
			for var in expand_target.decl_vars:
				expand_target.raws[var.symbol.fullyname] = self.resolve_type_symbol(expand_target.raws, var).to.var(var)

		# シンボルテーブルを統合
		combine_raws = SymbolRaws.new()
		for expanded in expands.values():
			combine_raws.merge(expanded.raws)

		raws.merge(self.sorted_raws(combine_raws, [module.path for module in expands.keys()]))
		return raws

	def expand_module(self, module: Module) -> Expanded:
		"""モジュールの全シンボルを展開

		Args:
			module (Module): モジュール
		Returns:
			Expanded: 展開データ
		"""
		raws = SymbolRaws()
		decl_vars: list[defs.DeclVars] = []
		import_nodes: list[defs.Import] = []
		entrypoint = module.entrypoint.as_a(defs.Entrypoint)
		for node in entrypoint.flatten():
			if isinstance(node, defs.ClassDef):
				raws[node.fullyname] = Symbol(node)

			if type(node) is defs.Import:
				import_nodes.append(node)

			if isinstance(node, defs.Function):
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Enum:
				decl_vars.extend(node.vars)
			elif type(node) is defs.Class:
				decl_vars.extend(node.class_vars)
				decl_vars.extend(node.this_vars)
			elif isinstance(node, defs.Generator):
				decl_vars.extend(node.decl_vars)

		# XXX calculatedに含まれないためエントリーポイントは個別に処理
		decl_vars = [*entrypoint.decl_vars, *decl_vars]

		return Expanded(raws, decl_vars, import_nodes)

	def resolve_type_symbol(self, raws: SymbolRaws, var: defs.DeclVars) -> Reflection:
		"""シンボルテーブルから変数の型のシンボルを解決

		Args:
			raws (SymbolRaws): シンボルテーブル
			var (DeclVars): 変数宣言ノード
		Returns:
			SymbolRaw: シンボル
		"""
		decl_type = self.fetch_decl_type(var)
		if decl_type is not None:
			return self.finder.by_symbolic(raws, decl_type)
		else:
			return self.finder.by_standard(raws, classes.Unknown)

	def fetch_decl_type(self, var: defs.DeclVars) -> defs.Type | defs.ClassDef | None:
		"""変数の型(タイプ/クラス定義ノード)を取得。型が不明な場合はNoneを返却

		Args:
			var (DeclVars): 変数宣言ノード
		Returns:
			Type | ClassDef | None: タイプ/クラス定義ノード。不明な場合はNone
		"""
		if isinstance(var.declare, defs.Parameter):
			if isinstance(var.declare.symbol, defs.DeclClassParam):
				return var.declare.symbol.class_types.as_a(defs.ClassDef)
			elif isinstance(var.declare.symbol, defs.DeclThisParam):
				return var.declare.symbol.class_types.as_a(defs.ClassDef)
			else:
				return var.declare.var_type.as_a(defs.Type)
		elif isinstance(var.declare, (defs.AnnoAssign, defs.Catch)):
			return var.declare.var_type
		elif isinstance(var.declare, (defs.MoveAssign, defs.For, defs.CompFor)):
			# 型指定が無いため全てUnknown
			return None

		return None

	def sorted_raws(self, raws: SymbolRaws, module_orders: list[str]) -> dict[str, Reflection]:
		"""シンボルテーブルをモジュールのロード順に並び替え

		Args:
			raws (SymbolRaws): シンボルテーブル
			module_orders (list[str]): ロード順のモジュール名リスト
		Returns:
			dict[str, SymbolRaw]: 並び替え後のシンボルテーブル
		"""
		orders = {index: key for index, key in enumerate(module_orders)}
		def order(entry: tuple[str, Reflection]) -> int:
			key, _ = entry
			for index, module_path in orders.items():
				if module_path in key:
					return index

			return -1

		return dict(sorted(raws.items(), key=order))