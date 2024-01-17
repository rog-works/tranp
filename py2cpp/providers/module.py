from typing import cast

from py2cpp.lang.di import DI
from py2cpp.lang.locator import Currying, Locator
from py2cpp.module.types import ModulePath
from py2cpp.module.module import Module
from py2cpp.module.loader import ModuleLoader


def module_path_dummy() -> ModulePath:
	return ModulePath('__main__', '__main__')


def library_paths() -> list[str]:
	return ['py2cpp.compatible.python.classes']


def module_loader(locator: Locator) -> ModuleLoader:
	def handler(module_path: str) -> Module:
		di = cast(DI, locator).clone()
		di.rebind(Locator, lambda: di)
		di.rebind(Currying, lambda: di.currying)
		di.rebind(ModulePath, lambda: ModulePath(module_path, module_path))
		return di.resolve(Module)

	return handler
