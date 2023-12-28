import os
from typing import Callable, cast

from lark import Tree

from py2cpp.lang.di import DI
from py2cpp.lang.locator import Curry, Locator, T_Inst
from py2cpp.lang.module import load_module
from py2cpp.ast.entry import Entry
from py2cpp.ast.provider import Query, Settings
from py2cpp.ast.parser import FileLoader, GrammarSettings, SyntaxParser
from py2cpp.module.modules import Module, Modules
from py2cpp.module.provider import CoreLibrariesProvider
from py2cpp.node.classify import Classify
from py2cpp.node.definitions import make_settings
from py2cpp.node.node import Node
from py2cpp.node.nodes import NodeResolver, Nodes
from py2cpp.node.symboldb import SymbolDB, SymbolDBFactory
from py2cpp.tp_lark.entry import EntryOfLark
from py2cpp.tp_lark.parser import SyntaxParserOfLark


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
		self.__di: DI = self.__make_di()

	def __load_prebuild_tree(self, module_path: str) -> Entry:
		elems = module_path.split('.')
		dirpath, filename = '.'.join(elems[:-1]), elems[-1]
		fixture_path = '.'.join([dirpath, 'fixtures', filename])
		fixture = cast(Callable[[], Tree], load_module(fixture_path, 'fixture'))
		return EntryOfLark(fixture())

	def __core_libraries(self) -> list[str]:
		return ['tests.unit.py2cpp.node.fixtures.test_symboldb_classes']

	def __make_di(self) -> DI:
		di = DI()
		di.bind(Locator, lambda: di)
		di.bind(Curry, lambda: di.curry)
		di.bind(FileLoader, FileLoader)
		di.bind(GrammarSettings, lambda: GrammarSettings(grammar='data/grammar.lark'))
		di.bind(SyntaxParser, SyntaxParserOfLark)
		di.bind(CoreLibrariesProvider, lambda: self.__core_libraries)
		di.bind(Modules, Modules)
		di.bind(Module, lambda: Module(di, '__main__'))
		di.bind(Settings, make_settings)
		di.bind(Entry, lambda: self.__load_prebuild_tree(self.__module_path))
		di.bind(NodeResolver, NodeResolver)
		di.bind(Query[Node], Nodes)
		di.bind(Node, Nodes.root)
		di.bind(SymbolDB, SymbolDBFactory.create)
		di.bind(Classify, Classify)
		return di

	def get(self, symbol: type[T_Inst]) -> T_Inst:
		return self.__di.resolve(symbol)

	@property
	def main(self) -> Module:
		return self.__di.resolve(Module)

	@property
	def shared_nodes(self) -> Query[Node]:
		return self.__di.resolve(Query[Node])

	def custom_nodes(self, root: Entry) -> Query[Node]:
		di = self.__make_di()
		di.rebind(Entry, lambda: root)
		return di.resolve(Query[Node])
