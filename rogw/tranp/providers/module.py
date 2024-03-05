from typing import cast

from rogw.tranp.lang.di import DI, LazyDI
from rogw.tranp.lang.implementation import injectable
from rogw.tranp.lang.locator import Invoker, Locator
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.module.module import Module
from rogw.tranp.module.loader import ModuleDependencyProvider, ModuleLoader


def module_path_dummy() -> ModulePath:
	"""ダミーのモジュールパスを生成

	Returns:
		ModulePath: モジュールパス
	Note:
		モジュール経由で読み込みが不要な一部のテストでのみ利用
	"""
	return ModulePath('__main__', language='py')


def library_paths() -> ModulePaths:
	"""標準ライブラリーモジュールのパスリストを生成

	Returns:
		ModulePaths: モジュールパスリスト
	"""
	return ModulePaths([ModulePath('rogw.tranp.compatible.libralies.classes', language='py')])


def module_paths() -> ModulePaths:
	"""処理対象モジュールのパスリストを生成

	Returns:
		ModulePath: モジュールパスリスト
	"""
	return ModulePaths([ModulePath('example.example', language='py')])


@injectable
def module_loader(locator: Locator, dependency_provider: ModuleDependencyProvider) -> ModuleLoader:
	"""モジュールローダーを生成

	Args:
		locator (Locator): ロケーター @inject
		dependency_provider (ModuleDependencyProvider): @inject
	Returns:
		ModuleLoader: モジュールローダー
	"""
	def handler(module_path: ModulePath) -> Module:
		shared_di = cast(LazyDI, locator)
		dependency_di = LazyDI.instantiate(dependency_provider())
		new_di = shared_di.combine(dependency_di)
		new_di.rebind(DI, lambda: new_di)
		new_di.rebind(Invoker, lambda: new_di.invoke)
		new_di.bind(ModulePath, lambda: module_path)
		return new_di.resolve(Module)

	return handler
