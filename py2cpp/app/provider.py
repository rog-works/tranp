from py2cpp.lang.di import DI, LazyDI, ModuleDefinitions
from py2cpp.lang.locator import Currying, Locator


def di_container(definitions: ModuleDefinitions) -> DI:
	"""DIコンテナーを生成

	Args:
		definitions (ModuleDefinitions): モジュール定義
	Returns:
		DI: DIコンテナー
	"""
	di = LazyDI.instantiate(definitions)
	di.bind(Locator, lambda: di)
	di.bind(Currying, lambda: di.currying)
	return di
