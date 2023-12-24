from typing import Callable, TypeVar, cast

from py2cpp.ast.parser import SyntaxParser
from py2cpp.lang.locator import Locator
from py2cpp.node.base import Plugin
from py2cpp.node.node import Node
from py2cpp.node.nodes import Nodes
from py2cpp.tp_lark.types import Entry

T = TypeVar('T', bound=Node)


class ModuleLoader(Plugin):
	def __init__(self, locator: Locator, parser: SyntaxParser):
		self.__locator = locator
		self.__parser = parser

	def load(self, module_path: str, expect: type[T]) -> T:
		root = self.__parser.parse(module_path)
		factory = self.__locator.curry(Nodes, Callable[[Entry], Nodes])
		nodes = factory(root)
		return cast(expect, nodes.by('file_input'))  # XXX ダウンキャストと見做されて警告されるのでcastで対処
