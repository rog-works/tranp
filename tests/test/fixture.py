from typing import cast

from rogw.tranp.app.app import App
from rogw.tranp.app.io import appdir
from rogw.tranp.implements.syntax.lark.entry import EntryOfLark
from rogw.tranp.implements.syntax.lark.parser import SyntaxParserOfLark
from rogw.tranp.io.cache import CacheProvider
from rogw.tranp.lang.di import ModuleDefinitions
from rogw.tranp.lang.locator import T_Inst
from rogw.tranp.lang.module import filepath_to_module_path, fullyname
from rogw.tranp.module.module import Module
from rogw.tranp.module.modules import Modules
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.syntax.ast.parser import SyntaxParser
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
		module_path = filepath_to_module_path(filepath, appdir())
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
		self.__app = App({**self.__definitions(), **definitions})

	def __definitions(self) -> ModuleDefinitions:
		"""モジュール定義を生成

		Returns:
			ModuleDefinitions: モジュール定義
		"""
		return {fullyname(ModulePaths): lambda: [ModulePath(self.__fixture_module_path, language='py')]}

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
		return self.__app.resolve(Modules).load(self.__fixture_module_path)

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
		app = self.custom_app(source_code)
		custom_module_path = app.resolve(ModulePaths)[0]
		custom_module = app.resolve(Modules).load(custom_module_path.path)
		return custom_module.entrypoint.as_a(defs.Entrypoint).whole_by(full_path)

	def custom_app(self, source_code: str) -> App:
		"""ソースコードからカスタムアプリケーションを生成

		Args:
			source_code (str): ソースコード
		Returns:
			App: アプリケーション
		"""
		custom_module_path = ModulePath('__main__', language='py')

		def syntax_parser() -> SyntaxParser:
			org_parser = self.__app.resolve(SyntaxParser)
			lark = cast(SyntaxParserOfLark, org_parser).dirty_get_origin()
			root = EntryOfLark(lark.parse(f'{source_code}\n'))
			def new_parser(module_path: str) -> Entry:
				return root if module_path == custom_module_path.path else org_parser(module_path)

			return new_parser

		new_definitions = {
			fullyname(ModulePaths): lambda: [custom_module_path],
			fullyname(SyntaxParser): syntax_parser,
			fullyname(CacheProvider): lambda: self.__app.resolve(CacheProvider),
		}
		definitions = {**self.__definitions(), **new_definitions}
		return App(definitions)
