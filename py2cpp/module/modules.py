from typing import cast

from py2cpp.lang.di import DI
from py2cpp.lang.locator import Curry, Locator
from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import SyntaxParser
from py2cpp.module.module import Module
from py2cpp.module.provider import CoreLibrariesProvider


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
		return list(self.__modules.values())

	@property
	def core_libralies(self) -> list[Module]:
		paths = self.__locator.resolve(CoreLibrariesProvider)()
		return [self.load(path) for path in paths]

	def load(self, module_path: str) -> Module:
		if module_path not in self.__modules:
			self.__modules[module_path] = self.__load_impl(module_path)

		return self.__modules[module_path]

	def __load_impl(self, module_path: str) -> Module:
		root = self.__parser.parse(module_path)
		di = cast(DI, self.__locator).clone()
		di.unbind(Locator)
		di.unbind(Curry)
		di.unbind(Entry)
		di.unbind(Module)
		di.bind(Locator, lambda: di)
		di.bind(Curry, lambda: di.curry)
		di.bind(Module, lambda: Module(di, module_path))
		di.bind(Entry, lambda: root)
		return di.resolve(Module)
