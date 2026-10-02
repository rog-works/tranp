from tranp.app.implements.cpp.view.cpp_view_helper import factories_for_cpp
from tranp.app.view.helper.helper import factories
from tranp.app.view.render import RendererHelperProvider


def renderer_helper_provider_cpp() -> RendererHelperProvider:
	"""ヘルパープロバイダー(C++用)

	Returns:
		ヘルパープロバイダー
	"""
	funcs, filters = factories()
	funcs_cpp, filters_cpp = factories_for_cpp()
	return lambda: ([*funcs, *funcs_cpp], [*filters, *filters_cpp])
