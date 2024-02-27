from typing import Callable

from rogw.tranp.analyze.plugin import IPlugin, PluginProvider
from rogw.tranp.lang.implementation import injectable
from rogw.tranp.lang.locator import Currying


@injectable
def cpp_plugin_provider(currying: Currying) -> PluginProvider:
	"""プラグインプロバイダーを生成

	Args:
		currying: カリー化関数 @inject
	Returns:
		PluginProvider: プラグインプロバイダー
	"""
	classes: list[type[IPlugin]] = []
	return lambda: [currying(ctor, Callable[[], IPlugin])() for ctor in classes]
