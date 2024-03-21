import os

from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.app.env import Env
from rogw.tranp.lang.di import DI, LazyDI, ModuleDefinitions
from rogw.tranp.lang.locator import Invoker, Locator


def di_container(definitions: ModuleDefinitions) -> DI:
	"""DIコンテナーを生成

	Args:
		definitions (ModuleDefinitions): モジュール定義
	Returns:
		DI: DIコンテナー
	"""
	di = LazyDI.instantiate(definitions)
	di.bind(Locator, lambda: di)
	di.bind(Invoker, lambda: di.invoke)
	return di


def make_example_env() -> Env:
	"""環境変数を生成(example用)

	Returns:
		Env: 環境変数
	"""
	paths = [
		tranp_dir(),
		os.path.join(tranp_dir(), 'example')
	]
	return Env({
		'PYTHONPATH': {path: path for path in paths},
	})
