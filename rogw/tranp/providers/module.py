from typing import cast

from rogw.tranp.lang.di import LazyDI
from rogw.tranp.lang.implementation import injectable
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
	return ModulePath('__main__', language='py')


def library_paths() -> list[ModulePath]:
	"""標準ライブラリーモジュールのパスリストを生成

	Returns:
		list[ModulePath]: モジュールパスリスト
	"""
	return [ModulePath('rogw.tranp.compatible.libralies.classes', language='py')]


def module_paths() -> list[ModulePath]:
	"""処理対象モジュールのパスリストを生成

	Returns:
		list[ModulePath]: モジュールパスリスト
	"""
	return [ModulePath('example.example', language='py')]


@injectable
def module_loader(locator: Locator) -> ModuleLoader:
	"""モジュールローダーを生成

	Args:
		locator (Locator): ロケーター @inject
	Returns:
		ModuleLoader: モジュールローダー
	"""
	def handler(module_path: ModulePath) -> Module:
		di = cast(LazyDI, locator).clone()
		di.rebind(Locator, lambda: di)
		di.rebind(Invoker, lambda: di.invoke)
		di.bind(ModulePath, lambda: module_path)
		# FIXME 修正
		di.register('rogw.tranp.module.module.Module', 'rogw.tranp.module.module.Module')
		di.register('rogw.tranp.syntax.ast.entry.Entry', 'rogw.tranp.providers.ast.make_entrypoint')
		di.register('rogw.tranp.syntax.ast.query.Query', 'rogw.tranp.syntax.node.query.Nodes')
		di.register('rogw.tranp.syntax.node.node.Node', 'rogw.tranp.providers.node.entrypoint')
		di.register('rogw.tranp.syntax.node.resolver.NodeResolver', 'rogw.tranp.syntax.node.resolver.NodeResolver')
		return di.resolve(Module)

	return handler
