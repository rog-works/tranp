from dataclasses import dataclass, field

from rogw.tranp.lang.implementation import injectable
from rogw.tranp.module.modules import Module, Modules
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.semantics.finder import SymbolFinder
from rogw.tranp.semantics.reflection import SymbolRaws
from rogw.tranp.semantics.reflection_impl import Symbol


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


class ExpandModules:
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
		# モジュールを展開
		load_index = 0
		load_reserves = {modules.main.path: True}
		expanded_modules: dict[str, Expanded] = {}
		while load_index < len(load_reserves):
			module_path = list(load_reserves.keys())[load_index]
			module = modules.load(module_path)
			expanded = self.expand_module(module)
			load_reserves = {**load_reserves, **{node.import_path.tokens: True for node in expanded.import_nodes}}
			expanded_modules[module_path] = expanded

		# シンボルテーブルを統合
		combine_raws = SymbolRaws.new()
		for expanded in expanded_modules.values():
			combine_raws.merge(expanded.raws)

		raws.merge(combine_raws.sorted([module_path for module_path in expanded_modules.keys()]))
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
