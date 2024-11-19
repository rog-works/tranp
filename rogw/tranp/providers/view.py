from rogw.tranp.view.helper.helper import factories, factories_for_cpp
from rogw.tranp.view.render import RendererHelperProvider, RendererSetting


def cpp_renderer_helper_provider(setting: RendererSetting) -> RendererHelperProvider:
	"""ヘルパープロバイダー(C++用)

	Args:
		setting (RendererSetting): テンプレートレンダー設定データ
	Returns:
		RendererHelperProvider: ヘルパープロバイダー
	"""
	funcs, filters = factories()
	funcs_cpp, filters_cpp = factories_for_cpp()
	return lambda: {
		'function': {factory.__name__: factory(setting) for factory in [*funcs, *funcs_cpp]},
		'filter': {factory.__name__: factory(setting) for factory in [*filters, *filters_cpp]},
	}
