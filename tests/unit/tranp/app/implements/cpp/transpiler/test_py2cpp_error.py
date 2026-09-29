import os
import re
from unittest import TestCase

from tests.test.fixture import Fixture
from tranp.app.app.dir import tranp_dir
from tranp.app.dsn.module import ModuleDSN
from tranp.app.errors import Errors
from tranp.app.i18n.i18n import I18n
from tranp.app.implements.cpp.providers.view import renderer_helper_provider_cpp
from tranp.app.implements.cpp.transpiler.py2cpp import Py2Cpp
from tranp.app.lang.middleware import Middleware
from tranp.app.lang.module import to_fullyname
from tranp.app.semantics.reflections import Reflections
from tranp.app.test.helper import data_provider
from tranp.app.transpiler.types import TranspilerOptions
from tranp.app.view.render import Renderer, RendererEmitter, RendererHelperProvider, RendererSetting


def make_renderer_setting(i18n: I18n, emitter: RendererEmitter) -> RendererSetting:
	template_dir = [os.path.join(tranp_dir(), 'data', 'cpp', 'template')]
	env = {'immutable_param_types': ['std::string', 'std::vector', 'std::map', 'std::function']}
	return RendererSetting(template_dir, i18n.t, emitter, env)


class TestPy2CppError(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__, {
		to_fullyname(Py2Cpp): Py2Cpp,
		to_fullyname(Renderer): Renderer,
		to_fullyname(RendererEmitter): Middleware,
		to_fullyname(RendererHelperProvider): renderer_helper_provider_cpp,
		to_fullyname(RendererSetting): make_renderer_setting,
		to_fullyname(TranspilerOptions): lambda: TranspilerOptions(verbose=False, env={}),
	})

	@data_provider([
		('InvalidOps.ternary_to_union_types', 'function_def_raw.block.assign', Errors.OperationNotAllowed, 'Must be Nullable or Non-Union'),
		('InvalidOps.destruction_assign', 'function_def_raw.block.assign', Errors.OperationNotAllowed, 'Must be a tuple'),
	])
	def test_exec(self, local_path: str, offset_path: str, expected_error: type[Exception], expected: re.Pattern) -> None:
		with self.assertRaisesRegex(expected_error, expected):
			self.fixture.shared_module
			via_node = self.fixture.get(Reflections).from_fullyname(ModuleDSN.full_joined(self.fixture_module_path, local_path)).node
			node = self.fixture.shared_module.entrypoint.whole_by(ModuleDSN.local_joined(via_node.full_path, offset_path))
			self.fixture.get(Py2Cpp).transpile(node)
