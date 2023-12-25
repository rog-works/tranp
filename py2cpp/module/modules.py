from typing import cast

from py2cpp.lang.di import DI
from py2cpp.lang.locator import Curry, Locator
from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import SyntaxParser
from py2cpp.module.module import Module


class Modules:
	def __init__(self, locator: Locator, parser: SyntaxParser) -> None:
		self.__modules: dict[str, Module] = {}
		self.__locator = locator
		self.__parser = parser

	@property
	def main(self) -> Module:
		return self.__locator.resolve(Module)  # FIXME Modules以外がモジュールを管理しているのはおかしい

	@property
	def imported(self) -> list[Module]:
		self.__implicit_modules()  # FIXME 何かしらトリガーを用意
		return [value for key, value in self.__modules.items() if key != '__main__']

	def __implicit_modules(self) -> list[Module]:
		paths = ['py2cpp.python.classes']
		return [self.load(path) for path in paths]

	def load(self, module_path: str) -> Module:
		if module_path not in self.__modules:
			self.__modules[module_path] = self.__load_impl(module_path)

		return self.__modules[module_path]

	def __load_impl(self, module_path: str) -> Module:
		root = self.__parser.parse(module_path)
		di = cast(DI, self.__locator).clone()
		di.unregister(Locator)
		di.unregister(Curry)
		di.unregister(Entry)
		di.unregister(Module)
		di.register(Locator, lambda: di)
		di.register(Curry, lambda: di.curry)
		di.register(Module, lambda: Module(di, module_path))
		di.register(Entry, lambda: root)
		return di.resolve(Module)
