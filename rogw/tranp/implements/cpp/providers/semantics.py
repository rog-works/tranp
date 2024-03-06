from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.locator import Invoker
from rogw.tranp.semantics.plugin import IPlugin, PluginProvider


@injectable
def cpp_plugin_provider(invoker: Invoker) -> PluginProvider:
	"""プラグインプロバイダーを生成

	Args:
		invoker: ファクトリー関数 @inject
	Returns:
		PluginProvider: プラグインプロバイダー
	"""
	classes: list[type[IPlugin]] = []
	return lambda: [invoker(ctor) for ctor in classes]
