import os
from typing import Callable, cast

from lark import Lark, Tree
from lark.indenter import PythonIndenter

from py2cpp.lang.di import DI
from py2cpp.lang.locator import Locator
from py2cpp.lang.module import load_module
from py2cpp.ast.provider import Query, Settings
from py2cpp.node.definitions import make_settings
from py2cpp.node.node import Node
from py2cpp.node.nodes import NodeResolver, Nodes
from py2cpp.tp_lark.types import Entry


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

	def __load_parser(self) -> Lark:
		grammar_path = os.path.join(self.__appdir(), 'data/grammar.lark')
		with open(grammar_path, mode='r') as f:
			return Lark(f, start='file_input', postlex=PythonIndenter(), parser='lalr')

	def __load_source(self, module_path: str) -> str:
		filepath = module_path.replace('.', '/')
		source_path = os.path.join(self.__appdir(), f'{filepath}_fixture.org.py')
		with open(source_path, mode='r') as f:
			return '\n'.join(f.readlines())

	def __build_tree(self, module_path: str) -> Tree:
		parser = self.__load_parser()
		source = self.__load_source(module_path)
		return parser.parse(source)

	def __load_prebuild_tree(self, module_path: str) -> Tree:
		fixture_path = f'{module_path}_fixture'
		fixture = cast(Callable[[], Tree], load_module(fixture_path, 'fixture'))
		return fixture()


	def __make_di(self) -> DI:
		di = DI()
		di.register(Locator, lambda: di)
		di.register(Settings, make_settings)
		di.register(NodeResolver, NodeResolver)
		di.register(Query[Node], Nodes)
		return di

	@property
	def shared(self) -> Query[Node]:
		if not self.__di.can_resolve(Entry):
			self.__di.register(Entry, lambda: self.__load_prebuild_tree(self.__module_path))

		return self.__di.resolve(Query[Node])

	def custom(self, tree: Tree) -> Query[Node]:
		di = self.__make_di()
		di.register(Entry, lambda: tree)
		return di.resolve(Query[Node])
