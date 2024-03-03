from rogw.tranp.lang.implementation import injectable
from rogw.tranp.module.modules import Module, Modules
from rogw.tranp.semantics.reflection import SymbolRaws
import rogw.tranp.syntax.node.definition as defs


class ExpandModules:
	"""モジュールからシンボルテーブルの生成
	
	Note:
		プリプロセッサーの最初に実行することが前提
	"""

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
		raw_map: dict[str, str] = {}
		while load_index < len(load_reserves):
			module_path = list(load_reserves.keys())[load_index]
			module = modules.load(module_path)
			expanded_map, import_paths = self.expand_module(module)
			load_reserves = {**load_reserves, **{import_path: True for import_path in import_paths}}
			raw_map = {**raw_map, **expanded_map}

		# FIXME impl

		return raws

	def expand_module(self, module: Module) -> tuple[dict[str, str], list[str]]:
		"""モジュールのシンボル・インポートパスを展開

		Args:
			module (Module): モジュール
		Returns:
			tuple[dict[str, str], list[str]]: (シンボルマップ, インポートパスリスト)
		"""
		nodes = module.entrypoint.flatten()
		nodes.append(module.entrypoint)

		raw_map: dict[str, str] = {}
		import_paths: list[str] = []
		for node in nodes:
			if isinstance(node, defs.ClassDef):
				raw_map[node.fullyname] = node.full_path

			if isinstance(node, defs.Import):
				raw_map = {**raw_map, **{symbol.fullyname: symbol.full_path for symbol in node.import_symbols}}

			if isinstance(node, defs.Entrypoint):
				raw_map = {**raw_map, **{var.fullyname: var.full_path for var in node.decl_vars}}
			elif isinstance(node, defs.Function):
				raw_map = {**raw_map, **{var.fullyname: var.full_path for var in node.decl_vars}}
			elif isinstance(node, defs.Enum):
				raw_map = {**raw_map, **{var.fullyname: var.full_path for var in node.vars}}
			elif isinstance(node, defs.Class):
				raw_map = {**raw_map, **{var.fullyname: var.full_path for var in node.class_vars}}
				raw_map = {**raw_map, **{var.fullyname: var.full_path for var in node.this_vars}}
			elif isinstance(node, defs.Generator):
				raw_map = {**raw_map, **{var.fullyname: var.full_path for var in node.decl_vars}}

			if isinstance(node, defs.Import):
				import_paths.append(node.import_path.tokens)

		return raw_map, import_paths
