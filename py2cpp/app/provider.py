from py2cpp.app.types import ModuleDefinitions
from py2cpp.lang.di import DI
from py2cpp.lang.locator import Currying, Locator
from py2cpp.lang.module import load_module_path


def di_container(config: ModuleDefinitions) -> DI:
	di = DI()
	di.bind(Locator, lambda: di)
	di.bind(Currying, lambda: di.currying)
	for symbol, injector in config.items():
		di.bind(load_module_path(symbol), injector if callable(injector) else load_module_path(injector))

	return di
