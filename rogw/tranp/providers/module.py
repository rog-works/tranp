from typing import cast

from rogw.tranp.lang.di import DI
from rogw.tranp.lang.locator import Invoker, Locator
from rogw.tranp.module.types import ModulePath
from rogw.tranp.module.module import Module
from rogw.tranp.module.loader import ModuleLoader


def module_path_dummy() -> ModulePath:
	"""ダミーのモジュールパスを生成

	Returns:
		ModulePath: モジュールパス
	Note:
		モジュール経由で読み込みが不要な一部のテストでのみ利用
	"""
	return ModulePath('__main__', '__main__')


def library_paths() -> list[str]:
	"""標準ライブラリーのパスリストを生成

	Returns:
		list[str]: パスリスト
	"""
	return ['rogw.tranp.compatible.libralies.classes']


def module_loader(locator: Locator) -> ModuleLoader:
	"""モジュールローダーを生成

	Args:
		locator (Locator): ロケーター
	Returns:
		ModuleLoader: モジュールローダー
	"""
	def handler(module_path: str) -> Module:
		di = cast(DI, locator).clone()
		di.rebind(Locator, lambda: di)
		di.rebind(Invoker, lambda: di.invoke)
		di.rebind(ModulePath, lambda: ModulePath(module_path, module_path))
		return di.resolve(Module)

	return handler
