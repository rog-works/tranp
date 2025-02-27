from rogw.tranp.view.helper.helper import factories, factories_for_cpp
from rogw.tranp.view.render import RendererHelperProvider, RendererSetting


def renderer_helper_provider_cpp(setting: RendererSetting) -> RendererHelperProvider:
	"""ヘルパープロバイダー(C++用)

	Args:
		setting: テンプレートレンダー設定データ
	Returns:
		ヘルパープロバイダー
	"""
	funcs, filters = factories()
	funcs_cpp, filters_cpp = factories_for_cpp()
	return lambda: {
		'function': {factory.__name__: factory(setting) for factory in [*funcs, *funcs_cpp]},
		'filter': {factory.__name__: factory(setting) for factory in [*filters, *filters_cpp]},
	}
