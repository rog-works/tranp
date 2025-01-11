import hashlib

from rogw.tranp.lang.annotation import injectable
from rogw.tranp.module.module import Module
from rogw.tranp.module.loader import IModuleLoader
from rogw.tranp.module.types import LibraryPaths, ModulePath, ModulePaths


class Modules:
	"""モジュールマネージャー。全ての依存モジュールを管理"""

	@injectable
	def __init__(self, library_paths: LibraryPaths, module_paths: ModulePaths, loader: IModuleLoader) -> None:
		"""インスタンスを生成

		Args:
			library_paths: 標準ライブラリーパスリスト @inject
			module_paths: 処理対象モジュールパスリスト @inject
			loader: モジュールローダー @inject
		"""
		self.__library_paths = library_paths
		self.__module_paths = module_paths
		self.__loader = loader
		self.__modules: dict[str, Module] = {}

	def libralies(self) -> list[Module]:
		"""標準ライブラリーのモジュールリストを取得

		Returns:
			list[Module]: モジュールリスト
		"""
		return [self.load(module_path.path, module_path.language) for module_path in self.__library_paths]

	def targets(self) -> list[Module]:
		"""処理対象のモジュールリストを取得

		Returns:
			list[Module]: モジュールリスト
		"""
		return [self.load(module_path.path, module_path.language) for module_path in self.__module_paths]

	def dependencies(self) -> list[Module]:
		"""標準ライブラリーと処理対象のモジュールリストを取得

		Returns:
			list[Module]: モジュールリスト
		"""
		return [*self.libralies(), *self.targets()]

	def loaded(self) -> list[Module]:
		"""読み込み済みの全てのモジュールリストを取得

		Returns:
			list[Module]: モジュールリスト
		"""
		return list(self.__modules.values())

	def load(self, module_path: str, language: str = 'py') -> Module:
		"""モジュールをロード

		Args:
			module_path: モジュールパス
			language: 言語タグ (default = 'py')
		Returns:
			Module: モジュール
		Note:
			* ロードしたモジュールはパスとマッピングしてキャッシュ
			* 依存モジュールを再帰的にロードする
		"""
		if module_path not in self.__modules:
			self.__load_libraries(module_path)
			self.__modules[module_path] = self.__loader.load(ModulePath(module_path, language))
			self.__load_dependencies(self.__modules[module_path])
			self.__loader.preprocess(self.__modules[module_path])

		return self.__modules[module_path]

	def __load_libraries(self, via_module_path: str) -> None:
		"""標準ライブラリーをロード

		Args:
			via_module_path: 読み込み中のモジュールパス
		Note:
			読み込み中のモジュールが標準ライブラリー以外の場合のみロード
		"""
		if via_module_path not in [path.path for path in self.__library_paths]:
			self.libralies()

	def __load_dependencies(self, via_module: Module) -> None:
		"""依存モジュールをロード

		Args:
			via_module: 読み込み中のモジュール
		"""
		for import_node in via_module.entrypoint.imports:
			self.load(import_node.import_path.tokens)

	def identity(self) -> str:
		"""モジュール全体から一意な識別子を生成

		Args:
			str: 一意な識別子
		Note:
			モジュールを全てロードするため、非常に高負荷になり得る。なるべく使用しないことを推奨
		"""
		self.dependencies()
		identities = [module.identity() for module in self.loaded()]
		return hashlib.md5(str(identities).encode('utf-8')).hexdigest()

	def unload(self, module_path: str) -> None:
		"""指定のモジュールをアンロード

		Args:
			module_path: モジュールパス
		"""
		if module_path in self.__modules:
			module = self.__modules[module_path]
			self.__loader.unload(module.module_path)
			del self.__modules[module_path]
