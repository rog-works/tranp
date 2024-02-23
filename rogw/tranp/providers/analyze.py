from rogw.tranp.analyze.plugin import PluginProvider


def plugin_provider() -> PluginProvider:
	"""プラグインプロバイダーを生成

	Returns:
		PluginProvider: プラグインプロバイダー
	"""
	return lambda: []
