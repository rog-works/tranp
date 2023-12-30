from py2cpp.lang.di import DI, LazyDI, ModuleDefinitions
from py2cpp.lang.locator import Currying, Locator


def di_container(config: ModuleDefinitions) -> DI:
	di = LazyDI.instantiate(config)
	di.bind(Locator, lambda: di)
	di.bind(Currying, lambda: di.currying)
	return di
