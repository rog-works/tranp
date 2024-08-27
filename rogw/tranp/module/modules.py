import hashlib

from rogw.tranp.lang.annotation import injectable
from rogw.tranp.module.module import Module
from rogw.tranp.module.loader import ModuleLoader
from rogw.tranp.module.types import LibraryPaths, ModulePath, ModulePaths
from rogw.tranp.semantics.reflection.db import SymbolDB


class Modules:
	"""モジュールマネージャー。全ての依存モジュールを管理"""

	@injectable
	def __init__(self, library_paths: LibraryPaths, module_paths: ModulePaths, db: SymbolDB, loader: ModuleLoader) -> None:
		"""インスタンスを生成

		Args:
			library_paths (LibraryPaths): 標準ライブラリーパスリスト @inject
			module_paths (ModulePaths): 処理対象モジュールパスリスト @inject
			db (SymbolDB): シンボルテーブル @inject
			loader (ModuleLoader): モジュールローダー @inject
		"""
		self.__library_paths = library_paths
		self.__module_paths = module_paths
		self.__db = db
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

	def identity(self) -> str:
		"""依存モジュール全体から一意な識別子を生成

		Args:
			str: 一意な識別子
		"""
		identities = ','.join([module.identity() for module in self.dependencies()])
		return hashlib.md5(identities.encode('utf-8')).hexdigest()

	def unload(self, module_path: str) -> None:
		"""指定のモジュールをアンロード

		Args:
			module_path (str): モジュールパス
		"""
		if module_path in self.__modules:
			del self.__modules[module_path]
			self.__db.unload(module_path)
