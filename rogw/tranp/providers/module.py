from typing import cast

from rogw.tranp.lang.di import DI
from rogw.tranp.lang.locator import Currying, Locator
from rogw.tranp.module.types import ModulePath
from rogw.tranp.module.module import Module
from rogw.tranp.module.loader import ModuleLoader


def module_path_dummy() -> ModulePath:
	return ModulePath('__main__', '__main__')


def library_paths() -> list[str]:
	return ['rogw.tranp.compatible.python.classes']


def module_loader(locator: Locator) -> ModuleLoader:
	def handler(module_path: str) -> Module:
		di = cast(DI, locator).clone()
		di.rebind(Locator, lambda: di)
		di.rebind(Currying, lambda: di.currying)
		di.rebind(ModulePath, lambda: ModulePath(module_path, module_path))
		return di.resolve(Module)

	return handler
