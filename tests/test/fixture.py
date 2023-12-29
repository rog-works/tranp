import os
from typing import Callable, cast

from lark import Tree

from py2cpp.lang.locator import T_Inst
from py2cpp.lang.module import load_module
from py2cpp.app.app import App
from py2cpp.app.types import ModuleDefinitions
from py2cpp.ast.entry import Entry
from py2cpp.ast.query import Query
from py2cpp.ast.parser import SyntaxParser
from py2cpp.module.module import Module
from py2cpp.module.types import ModulePath
from py2cpp.ast.provider import make_entrypoint
from py2cpp.node.node import Node
from py2cpp.tp_lark.entry import EntryOfLark


class Fixture:
	@classmethod
	def make(cls, filepath: str) -> 'Fixture':
		rel_path = filepath.split(cls.__appdir())[1]
		without_ext = rel_path.split('.')[0]
		elems =  [elem for elem in without_ext.split(os.path.sep) if elem]
		module_path = '.'.join(elems)
		return cls(module_path)

	@classmethod
	def __appdir(cls) -> str:
		return os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

	def __init__(self, module_path: str) -> None:
		self.__module_path = module_path
		self.__app = App(self.__definitions())

	def __definitions(self) -> ModuleDefinitions:
		return {
			'py2cpp.ast.entry.Entry': self.__make_entrypoint,
			'py2cpp.module.base.LibraryPaths': self.__library_paths,
		}

	def __library_paths(self) -> list[str]:
		return ['tests.unit.py2cpp.node.fixtures.test_symboldb_classes']

	def __make_entrypoint(self, module_path: ModulePath, parser: SyntaxParser) -> Entry:
		if module_path == '__main__':
			return self.__make_entrypoint_from_fixture()
		else:
			return make_entrypoint(module_path, parser)

	def __make_entrypoint_from_fixture(self) -> Entry:
		elems = self.__module_path.split('.')
		dirpath, filename = '.'.join(elems[:-1]), elems[-1]
		fixture_path = '.'.join([dirpath, 'fixtures', filename])
		fixture = cast(Callable[[], Tree], load_module(fixture_path, 'fixture'))
		return EntryOfLark(fixture())

	def get(self, symbol: type[T_Inst]) -> T_Inst:
		return self.__app.resolve(symbol)

	@property
	def main(self) -> Module:
		return self.__app.resolve(Module)

	@property
	def shared_nodes(self) -> Query[Node]:
		return self.__app.resolve(Query[Node])

	def custom_nodes(self, root: Entry) -> Query[Node]:
		definitions = {**self.__definitions(), **{'py2cpp.ast.entry.Entry': lambda: root}}
		return App(definitions).resolve(Query[Node])
