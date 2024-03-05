from rogw.tranp.lang.implementation import injectable
from rogw.tranp.module.module import Module
from rogw.tranp.module.loader import ModuleLoader
from rogw.tranp.module.types import LibraryPaths, ModulePath, ModulePaths


class Modules:
	"""モジュールマネージャー。処理対象のモジュールと依存モジュールを管理"""

	@injectable
	def __init__(self, library_paths: LibraryPaths, module_paths: ModulePaths, loader: ModuleLoader) -> None:
		"""インスタンスを生成

		Args:
			library_paths (LibraryPaths): 標準ライブラリーパスリスト @inject
			module_paths (ModulePaths): 処理対象モジュールパスリスト @inject
			loader (ModuleLoader): モジュールローダー @inject
		"""
		self.__library_paths = library_paths
		self.__module_paths = module_paths
		self.__loader = loader
		self.__modules: dict[str, Module] = {}

	@property
	def libralies(self) -> list[Module]:
		"""list[Module]: 標準ライブラリーモジュールリスト"""
		return [self.load(module_path.path, module_path.language) for module_path in self.__library_paths]

	@property
	def targets(self) -> list[Module]:
		"""list[Module]: 処理対象のモジュールリスト"""
		return [self.load(module_path.path, module_path.language) for module_path in self.__module_paths]

	@property
	def requirements(self) -> list[Module]:
		"""list[Module]: 必須モジュールリスト"""
		return [*self.libralies, *self.targets]

	def load(self, module_path: str, language: str = 'py') -> Module:
		"""モジュールをロード。ロードしたモジュールはパスとマッピングしてキャッシュ

		Args:
			module_path (str): モジュールパス
			language (str): 言語タグ (default = 'py')
		Returns:
			Module: モジュール
		"""
		if module_path not in self.__modules:
			self.__modules[module_path] = self.__loader(ModulePath(module_path, language))

		return self.__modules[module_path]
