import os
from typing import cast

from rogw.tranp.app.app import App
from rogw.tranp.app.io import appdir
from rogw.tranp.ast.entry import Entry
from rogw.tranp.ast.parser import SyntaxParser
from rogw.tranp.ast.query import Query
from rogw.tranp.io.cache import CacheProvider
from rogw.tranp.lang.di import ModuleDefinitions
from rogw.tranp.lang.locator import T_Inst
from rogw.tranp.lang.module import fullyname
from rogw.tranp.module.module import Module
from rogw.tranp.module.types import ModulePath
from rogw.tranp.node.node import Node
from rogw.tranp.tp_lark.entry import EntryOfLark
from rogw.tranp.tp_lark.parser import SyntaxParserOfLark


class Fixture:
	@classmethod
	def make(cls, filepath: str) -> 'Fixture':
		rel_path = filepath.split(appdir())[1]
		without_ext = rel_path.split('.')[0]
		elems =  [elem for elem in without_ext.split(os.path.sep) if elem]
		test_module_path = '.'.join(elems)
		return cls(test_module_path)

	def __init__(self, test_module_path: str) -> None:
		self.__test_module_path = test_module_path
		self.__app = App(self.__definitions())

	def __definitions(self) -> ModuleDefinitions:
		return {
			fullyname(ModulePath): self.__module_path,
		}

	def __module_path(self) -> ModulePath:
		elems = self.__test_module_path.split('.')
		dirpath, filename = '.'.join(elems[:-1]), elems[-1]
		fixture_module_path = '.'.join([dirpath, 'fixtures', filename])
		return ModulePath('__main__', fixture_module_path)

	def get(self, symbol: type[T_Inst]) -> T_Inst:
		return self.__app.resolve(symbol)

	@property
	def main(self) -> Module:
		return self.__app.resolve(Module)

	@property
	def shared_nodes(self) -> Query[Node]:
		return self.__app.resolve(Query[Node])

	def custom_nodes(self, source_code: str) -> Query[Node]:
		return self.custom_app(source_code).resolve(Query[Node])

	def custom_app(self, source_code: str) -> App:
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
