import os

from py2cpp.lang.env import Env
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


def make_env() -> Env:
	"""環境変数を生成

	Returns:
		Env: 環境変数
	"""
	paths = [os.path.join(os.getcwd(), 'example')]
	return Env({
		'PYTHONPATH': {path: path for path in paths},
	})
