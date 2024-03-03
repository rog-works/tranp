from rogw.tranp.lang.implementation import injectable
from rogw.tranp.module.modules import Module, Modules
from rogw.tranp.semantics.reflection import DB
import rogw.tranp.syntax.node.definition as defs


class ExpandModules:
	"""モジュールからシンボルテーブルの生成
	
	Note:
		プリプロセッサーの最初に実行することが前提
	"""

	@injectable
	def __call__(self, modules: Modules) -> DB[str]:
		"""シンボルテーブルを生成

		Args:
			modules (Modules): モジュールマネージャー @inject
		Returns:
			dict[str, str]: シンボルテーブル
		"""
		# モジュールを展開
		load_index = 0
		load_reserves = {modules.main.path: True}
		raws = DB()
		while load_index < len(load_reserves):
			module_path = list(load_reserves.keys())[load_index]
			module = modules.load(module_path)
			expanded_raws, import_paths = self.expand_module(module)
			load_reserves = {**load_reserves, **{import_path: True for import_path in import_paths}}
			raws = DB({**raws, **expanded_raws})

		return raws.sorted(list(raws.keys()))

	def expand_module(self, module: Module) -> tuple[dict[str, str], list[str]]:
		"""モジュールのシンボル・インポートパスを展開

		Args:
			module (Module): モジュール
		Returns:
			tuple[dict[str, str], list[str]]: (シンボルテーブル, インポートパスリスト)
		"""
		nodes = module.entrypoint.flatten()
		nodes.append(module.entrypoint)

		raws: dict[str, str] = {}
		import_paths: list[str] = []
		for node in nodes:
			if isinstance(node, defs.ClassDef):
				raws[node.fullyname] = node.full_path

			if isinstance(node, defs.Import):
				raws = {**raws, **{symbol.fullyname: symbol.full_path for symbol in node.import_symbols}}

			if isinstance(node, defs.Entrypoint):
				raws = {**raws, **{var.fullyname: var.full_path for var in node.decl_vars}}
			elif isinstance(node, defs.Function):
				raws = {**raws, **{var.fullyname: var.full_path for var in node.decl_vars}}
			elif isinstance(node, defs.Enum):
				raws = {**raws, **{var.fullyname: var.full_path for var in node.vars}}
			elif isinstance(node, defs.Class):
				raws = {**raws, **{var.fullyname: var.full_path for var in node.class_vars}}
				raws = {**raws, **{var.fullyname: var.full_path for var in node.this_vars}}
			elif isinstance(node, defs.Generator):
				raws = {**raws, **{var.fullyname: var.full_path for var in node.decl_vars}}

			if isinstance(node, defs.Import):
				import_paths.append(node.import_path.tokens)

		return raws, import_paths
