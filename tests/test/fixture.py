import os
from typing import cast

from rogw.tranp.app.app import App
from rogw.tranp.app.io import appdir
from rogw.tranp.implements.syntax.lark.entry import EntryOfLark
from rogw.tranp.implements.syntax.lark.parser import SyntaxParserOfLark
from rogw.tranp.io.cache import CacheProvider
from rogw.tranp.lang.di import ModuleDefinitions
from rogw.tranp.lang.locator import T_Inst
from rogw.tranp.lang.module import fullyname
from rogw.tranp.module.module import Module
from rogw.tranp.module.types import ModulePath
from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.syntax.ast.parser import SyntaxParser
from rogw.tranp.syntax.ast.query import Query
from rogw.tranp.syntax.node.node import Node


class Fixture:
	"""フィクスチャーマネージャー"""

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
		rel_path = filepath.split(appdir())[1]
		without_ext = rel_path.split('.')[0]
		elems =  [elem for elem in without_ext.split(os.path.sep) if elem]
		test_module_path = '.'.join(elems)
		return cls(test_module_path, definitions)

	def __init__(self, test_module_path: str, definitions: ModuleDefinitions) -> None:
		"""インスタンスを生成

		Args:
			test_module_path (str): テストファイルのモジュールパス
			definitions (ModuleDefinitions): モジュール定義
		"""
		self.__test_module_path = test_module_path
		self.__app = App({**self.__definitions(), **definitions})

	def __definitions(self) -> ModuleDefinitions:
		"""モジュール定義を生成

		Returns:
			ModuleDefinitions: モジュール定義
		"""
		return {fullyname(ModulePath): self.__module_path}

	def __module_path(self) -> ModulePath:
		"""メインモジュールのモジュールパスを取得

		Args:
			ModulePath: モジュールパス
		"""
		elems = self.__test_module_path.split('.')
		dirpath, filename = '.'.join(elems[:-1]), elems[-1]
		fixture_module_path = '.'.join([dirpath, 'fixtures', filename])
		return ModulePath(fixture_module_path, fixture_module_path)

	def get(self, symbol: type[T_Inst]) -> T_Inst:
		"""テスト用アプリケーションからシンボルに対応したインスタンスを取得

		Args:
			symbol (type[T_Inst]): シンボル
		Returns:
			T_Inst: インスタンス
		"""
		return self.__app.resolve(symbol)

	@property
	def main(self) -> Module:
		"""Module: メインモジュール"""
		return self.__app.resolve(Module)

	@property
	def shared_nodes(self) -> Query[Node]:
		"""Query[Node]: 共有フィクスチャーのノードクエリー"""
		return self.__app.resolve(Query[Node])

	def custom_nodes(self, source_code: str) -> Query[Node]:
		"""ソースコードをビルドし、ノードクエリーを生成

		Args:
			source_code (str): ソースコード
		Returns:
			Query[Node]: カスタムのノードクエリー
		"""
		return self.custom_app(source_code).resolve(Query[Node])

	def custom_app(self, source_code: str) -> App:
		"""ソースコードからカスタムアプリケーションを生成

		Args:
			source_code (str): ソースコード
		Returns:
			App: アプリケーション
		"""
		def syntax_parser() -> SyntaxParser:
			org_parser = self.__app.resolve(SyntaxParser)
			test_module_path = self.__app.resolve(ModulePath)
			lark = cast(SyntaxParserOfLark, org_parser).dirty_get_origin()
			root = EntryOfLark(lark.parse(f'{source_code}\n'))
			def new_parser(module_path: str) -> Entry:
				return root if module_path == test_module_path.actual else org_parser(module_path)

			return new_parser

		new_definitions = {
			fullyname(SyntaxParser): syntax_parser,
			fullyname(CacheProvider): lambda: self.__app.resolve(CacheProvider),
		}
		definitions = {**self.__definitions(), **new_definitions}
		return App(definitions)
