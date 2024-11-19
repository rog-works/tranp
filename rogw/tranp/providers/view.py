from collections.abc import Callable
from typing import Any

import rogw.tranp.view.helper.helper as helper_defs
from rogw.tranp.view.render import RendererHelperProvider, RendererSetting


def make_helper_provider_cpp(setting: RendererSetting) -> RendererHelperProvider:
	"""ヘルパープロバイダー(C++用)

	Args:
		setting (RendererSetting): テンプレートレンダー設定データ
	Returns:
		RendererHelperProvider: ヘルパープロバイダー
	"""
	globals_helpers: list[Callable[[RendererSetting], Callable[..., Any]]] = [
		helper_defs.break_last_block,
		helper_defs.decorator_query,
		helper_defs.env_get,
		helper_defs.i18n,
		helper_defs.parameter_parse,
		helper_defs.reg_fullmatch,
		helper_defs.reg_match,
		helper_defs.reg_replace,
	]
	filters_helpers: list[Callable[[RendererSetting], Callable[..., Any]]] = [
		helper_defs.filter_find,
		helper_defs.filter_replace,
		helper_defs.filter_match,
		helper_defs.filter_fullmatch,
	]
	return lambda: {
		'globals': {helper.__name__: helper(setting) for helper in globals_helpers},
		'filters': {helper.__name__: helper(setting) for helper in filters_helpers},
	}
