import os
from typing import cast

from py2cpp.app.app import App
from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import SyntaxParser
from py2cpp.ast.query import Query
from py2cpp.io.cache import CacheProvider
from py2cpp.lang.di import ModuleDefinitions
from py2cpp.lang.locator import T_Inst
from py2cpp.lang.module import fullyname
from py2cpp.module.module import Module
from py2cpp.module.types import ModulePath
from py2cpp.node.node import Node
from py2cpp.tp_lark.entry import EntryOfLark
from py2cpp.tp_lark.parser import SyntaxParserOfLark


class Fixture:
	@classmethod
	def make(cls, filepath: str) -> 'Fixture':
		rel_path = filepath.split(cls.__appdir())[1]
		without_ext = rel_path.split('.')[0]
		elems =  [elem for elem in without_ext.split(os.path.sep) if elem]
		test_module_path = '.'.join(elems)
		return cls(test_module_path)

	@classmethod
	def __appdir(cls) -> str:
		return os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

	def __init__(self, test_module_path: str) -> None:
		self.__test_module_path = test_module_path
		self.__app = App(self.__definitions())

	def __definitions(self) -> ModuleDefinitions:
		return {
			'py2cpp.module.types.ModulePath': self.__module_path,
			'py2cpp.module.types.LibraryPaths': self.__library_paths,
		}

	def __module_path(self) -> ModulePath:
		elems = self.__test_module_path.split('.')
		dirpath, filename = '.'.join(elems[:-1]), elems[-1]
		fixture_module_path = '.'.join([dirpath, 'fixtures', filename])
		return ModulePath('__main__', fixture_module_path)

	def __library_paths(self) -> list[str]:
		return ['tests.unit.py2cpp.analyze.fixtures.test_db_classes']

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
