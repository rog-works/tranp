import os
import re
from unittest import TestCase

from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.errors import Errors
from rogw.tranp.i18n.i18n import I18n
from rogw.tranp.implements.cpp.providers.semantics import plugin_provider_cpp
from rogw.tranp.implements.cpp.providers.view import renderer_helper_provider_cpp
from rogw.tranp.implements.cpp.transpiler.py2cpp import Py2Cpp
from rogw.tranp.lang.eventemitter import EventEmitter
from rogw.tranp.lang.module import to_fullyname
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.test.helper import data_provider
from rogw.tranp.transpiler.types import TranspilerOptions
from rogw.tranp.view.render import Renderer, RendererEmitter, RendererHelperProvider, RendererSetting
from tests.test.fixture import Fixture


def make_renderer_setting(i18n: I18n, emitter: RendererEmitter) -> RendererSetting:
	template_dir = [os.path.join(tranp_dir(), 'data/cpp/template')]
	env = {'immutable_param_types': ['std::string', 'std::vector', 'std::map', 'std::function']}
	return RendererSetting(template_dir, i18n.t, emitter, env)


class TestPy2CppError(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__, {
		to_fullyname(Py2Cpp): Py2Cpp,
		to_fullyname(PluginProvider): plugin_provider_cpp,
		to_fullyname(Renderer): Renderer,
		to_fullyname(RendererEmitter): EventEmitter,
		to_fullyname(RendererHelperProvider): renderer_helper_provider_cpp,
		to_fullyname(RendererSetting): make_renderer_setting,
		to_fullyname(TranspilerOptions): lambda: TranspilerOptions(verbose=False, env={}),
	})

	@data_provider([
		('InvalidOps.ternary_to_union_types', 'function_def_raw.block.assign', Errors.OperationNotAllowed, 'Must be Nullable or Non-Union'),
		('InvalidOps.yield_return', 'function_def_raw.block.yield_stmt', Errors.NotSupported, 'Denied yield return'),
		('InvalidOps.delete_relay', 'function_def_raw.block.del_stmt', Errors.OperationNotAllowed, 'Must be list or dict'),
		('InvalidOps.destruction_assign', 'function_def_raw.block.assign', Errors.OperationNotAllowed, 'Must be a tuple'),
	])
	def test_exec(self, local_path: str, offset_path: str, expected_error: type[Exception], expected: re.Pattern) -> None:
		with self.assertRaisesRegex(expected_error, expected):
			self.fixture.shared_module
			via_node = self.fixture.get(Reflections).from_fullyname(ModuleDSN.full_joined(self.fixture_module_path, local_path)).node
			node = self.fixture.shared_module.entrypoint.whole_by(ModuleDSN.local_joined(via_node.full_path, offset_path))
			self.fixture.get(Py2Cpp).transpile(node)
