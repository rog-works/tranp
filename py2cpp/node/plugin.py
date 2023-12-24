from dataclasses import dataclass
from typing import Callable, TypeVar, cast

from lark import Lark
from lark.indenter import PythonIndenter

from py2cpp.lang.locator import Locator
from py2cpp.node.base import Plugin
from py2cpp.node.node import Node
from py2cpp.node.nodes import Nodes
from py2cpp.tp_lark.types import Entry

T = TypeVar('T', bound=Node)


@dataclass
class GrammarSettings:
	grammar: str
	start: str = 'file_input'
	algorihtem: str = 'lalr'


class FileLoader:
	def __call__(self, filepath: str) -> str:
		with open(filepath, mode='r') as f:
			return '\n'.join(f.readlines())


class SyntaxParser:
	def __init__(self, loader: FileLoader, settings: GrammarSettings) -> None:
		self.__loader = loader
		self.__settings = settings

	def parse(self, module_path: str) -> Entry:
		parser = self.__load_parser()
		source = self.__load_source(module_path)
		return parser.parse(source)

	def __load_parser(self) -> Lark:
		grammar = self.__loader(self.__settings.grammar)
		return Lark(grammar, start=self.__settings.start, postlex=PythonIndenter(), parser=self.__settings.algorihtem)

	def __load_source(self, module_path: str) -> str:
		filepath = module_path.replace('.', '/')
		source_path = f'{filepath}.py'
		return self.__loader(source_path)


class ModuleProvider(Plugin):
	def __init__(self, locator: Locator, parser: SyntaxParser):
		self.__locator = locator
		self.__parser = parser

	def provide(self, module_path: str, expect: type[T]) -> T:
		root = self.__parser.parse(module_path)
		factory = self.__locator.curry(Nodes, Callable[[Entry], Nodes])
		nodes = factory(root)
		return cast(expect, nodes.by('file_input'))  # XXX ダウンキャストと見做されて警告されるのでcastで対処
