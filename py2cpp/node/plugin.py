from typing import TypeVar

from py2cpp.module.modules import Modules
from py2cpp.node.base import Plugin
from py2cpp.node.node import Node

T = TypeVar('T', bound=Node)


class ModuleLoader(Plugin):
	def __init__(self, modules: Modules):
		self.__modules = modules

	def load(self, module_path: str, expect: type[T]) -> T:
		module = self.__modules.load(module_path)
		node = module.entrypoint(Node)
		if isinstance(node, expect):
			return node

		raise ValueError(f'Unexpected root node. module_path: {module_path}, expect: {expect}, actual: {node}')
