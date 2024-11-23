from rogw.tranp.app.app import App
from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.app.env import SourceEnvPath
from rogw.tranp.lang.annotation import duck_typed
from rogw.tranp.lang.di import ModuleDefinitions
from rogw.tranp.lang.locator import Invoker, T_Inst
from rogw.tranp.lang.module import filepath_to_module_path, to_fullyname
from rogw.tranp.module.module import Module
from rogw.tranp.module.modules import Modules
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.providers.module import module_path_dummy
from rogw.tranp.providers.syntax.ast import source_provider
from rogw.tranp.syntax.ast.entrypoints import Entrypoints
from rogw.tranp.syntax.ast.parser import SourceProvider
from rogw.tranp.syntax.node.node import Node


class Fixture:
	"""フィクスチャーマネージャー"""

	@classmethod
	def fixture_module_path(cls, filepath: str) -> str:
		"""フィクスチャーのモジュールパスを取得

		Args:
			filepath (str): テストファイルのパス
		Returns:
			str: フィクスチャーのモジュールパス
		"""
		module_path = filepath_to_module_path(filepath, tranp_dir())
		elems = module_path.split('.')
		dirpath, filename = '.'.join(elems[:-1]), elems[-1]
		return '.'.join([dirpath, 'fixtures', filename])

	@classmethod
	def make(cls, filepath: str, definitions: ModuleDefinitions = {}) -> 'Fixture':
		"""インスタンスを生成

		Args:
			filepath (str): テストファイルのパス
			definitions (ModuleDefinitions): モジュール定義 (default = {})
		Returns:
			Fixture: インスタンス
		Examples:
			```python
			class TestClass:
				fixture = Fixture.make(__file__)
			```
		"""
		return cls(cls.fixture_module_path(filepath), definitions)

	def __init__(self, fixture_module_path: str, definitions: ModuleDefinitions) -> None:
		"""インスタンスを生成

		Args:
			fixture_module_path (str): フィクスチャーのモジュールパス
			definitions (ModuleDefinitions): モジュール定義
		"""
		self.__fixture_module_path = fixture_module_path
		self.__custom_source_code = ''
		self.__app = App({**self.__definitions(), **definitions})

	def __definitions(self) -> ModuleDefinitions:
		"""モジュール定義を生成

		Returns:
			ModuleDefinitions: モジュール定義
		"""
		return {
			to_fullyname(ModulePaths): lambda: [ModulePath(self.__fixture_module_path, language='py')],
			to_fullyname(SourceProvider): lambda: self.__source_code_provider,
		}

	def get(self, symbol: type[T_Inst]) -> T_Inst:
		"""テスト用アプリケーションからシンボルに対応したインスタンスを取得

		Args:
			symbol (type[T_Inst]): シンボル
		Returns:
			T_Inst: インスタンス
		"""
		return self.__app.resolve(symbol)

	@property
	def shared_module(self) -> Module:
		"""Module: 共有フィクスチャーモジュール"""
		return self.get(Modules).load(self.__fixture_module_path)

	def shared_nodes_by(self, full_path: str) -> Node:
		"""共有フィクスチャーのノードを取得

		Args:
			full_path (str): フルパス
		Returns:
			Node: ノード
		"""
		return self.get(Entrypoints).load(self.__fixture_module_path).whole_by(full_path)

	def custom_nodes_by(self, source_code: str, full_path: str) -> Node:
		"""カスタムフィクスチャーのノードを取得

		Args:
			source_code (str): ソースコード
			full_path (str): フルパス
		Returns:
			Node: ノード
		"""
		module_path = module_path_dummy()
		self.__custom_source_code = f'{source_code}\n'
		entrypoints = self.get(Entrypoints)
		entrypoints.unload(module_path.path)
		return entrypoints.load(module_path.path).whole_by(full_path)

	def custom_module(self, source_code: str) -> Module:
		"""カスタムフィクスチャーのモジュールを取得

		Args:
			source_code (str): ソースコード
		Returns:
			Module: モジュール
		"""
		module_path = module_path_dummy()
		self.__custom_source_code = f'{source_code}\n'
		modules = self.get(Modules)
		modules.unload(module_path.path)
		return modules.load(module_path.path)

	@duck_typed(SourceProvider)
	def __source_code_provider(self, module_path: str) -> str:
		"""モジュールパスを基にソースコードを生成

		Args:
			module_path (str): モジュールパス
		Returns:
			str: ソースコード
		"""
		if module_path == module_path_dummy().path:
			return self.__custom_source_code
		else:
			return self.get(Invoker)(source_provider)(module_path)
