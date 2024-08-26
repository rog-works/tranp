from rogw.tranp.app.app import App
from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.lang.annotation import duck_typed
from rogw.tranp.lang.di import ModuleDefinitions
from rogw.tranp.lang.locator import Invoker, T_Inst
from rogw.tranp.lang.module import filepath_to_module_path, fullyname
from rogw.tranp.module.module import Module
from rogw.tranp.module.modules import Modules
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.providers.module import module_path_dummy
from rogw.tranp.providers.syntax.ast import source_code_provider
from rogw.tranp.semantics.processor import Preprocessors
from rogw.tranp.syntax.ast.parser import SourceCodeProvider
import rogw.tranp.syntax.node.definition as defs
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

	@classmethod
	def make_for_syntax(cls, filepath: str, definitions: ModuleDefinitions = {}) -> 'Fixture':
		"""インスタンスを生成

		Args:
			filepath (str): テストファイルのパス
			definitions (ModuleDefinitions): モジュール定義 (default = {})
		Returns:
			Fixture: インスタンス
		Examples:
			@see Fixture.make
		"""
		preprocessors_empty: Preprocessors = lambda: []
		_definitions = {fullyname(Preprocessors): lambda: preprocessors_empty}
		return cls(cls.fixture_module_path(filepath), {**_definitions, **definitions})

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
			fullyname(ModulePaths): lambda: [ModulePath(self.__fixture_module_path, language='py')],
			fullyname(SourceCodeProvider): lambda: self.__source_code_provider,
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
		return self.shared_module.entrypoint.as_a(defs.Entrypoint).whole_by(full_path)

	def custom_nodes_by(self, source_code: str, full_path: str) -> Node:
		"""共有フィクスチャーのノードを取得

		Args:
			source_code (str): ソースコード
			full_path (str): フルパス
		Returns:
			Node: ノード
		"""
		module_path = module_path_dummy()
		self.__custom_source_code = f'{source_code}\n'
		modules = self.get(Modules)
		modules.unload(module_path.path)
		return modules.load(module_path.path).entrypoint.as_a(defs.Entrypoint).whole_by(full_path)

	@duck_typed(SourceCodeProvider)
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
			return self.get(Invoker)(source_code_provider)(module_path)
