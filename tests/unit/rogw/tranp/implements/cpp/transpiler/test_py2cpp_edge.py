import os
import sys
from unittest import TestCase

import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.file.loader import IDataLoader
from rogw.tranp.i18n.i18n import I18n, TranslationMapping
from rogw.tranp.implements.cpp.providers.i18n import translation_mapping_cpp
from rogw.tranp.implements.cpp.providers.semantics import plugin_provider_cpp
from rogw.tranp.implements.cpp.providers.view import renderer_helper_provider_cpp
from rogw.tranp.implements.cpp.transpiler.py2cpp import Py2Cpp
from rogw.tranp.lang.eventemitter import EventEmitter
from rogw.tranp.lang.module import to_fullyname
from rogw.tranp.lang.profile import profiler
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.test.helper import data_provider
from rogw.tranp.transpiler.types import TranspilerOptions
from rogw.tranp.view.render import Renderer, RendererEmitter, RendererHelperProvider, RendererSetting
from tests.test.fixture import Fixture

profiler_on = '--' in sys.argv


def fixture_translation_mapping(datums: IDataLoader) -> TranslationMapping:
	return translation_mapping_cpp(datums)


def make_renderer_setting(i18n: I18n, emitter: RendererEmitter) -> RendererSetting:
	template_dirs = [os.path.join(tranp_dir(), 'data/cpp/template')]
	env = {'immutable_param_types': ['std::string', 'std::vector', 'std::map', 'std::function']}
	return RendererSetting(template_dirs, i18n.t, emitter, env)


class TestPy2CppEdge(TestCase):
	fixture_module_path = Fixture.fixture_module_path(__file__)
	fixture = Fixture.make(__file__, {
		to_fullyname(Py2Cpp): Py2Cpp,
		to_fullyname(PluginProvider): plugin_provider_cpp,
		to_fullyname(Renderer): Renderer,
		to_fullyname(RendererEmitter): EventEmitter,
		to_fullyname(RendererHelperProvider): renderer_helper_provider_cpp,
		to_fullyname(RendererSetting): make_renderer_setting,
		to_fullyname(TranslationMapping): fixture_translation_mapping,
		to_fullyname(TranspilerOptions): lambda: TranspilerOptions(verbose=False, env={}),
	})

	@profiler(on=profiler_on)
	@data_provider([
		('A.__init__', 'function_def_raw.block.funccall', defs.FuncCall, 'Action<T_Scalar>("hoge", "fuga", [](T_Args e) -> void { printf(e); });'),
	])
	def test_exec(self, local_path: str, offset_path: str, expected_type: type[Node], expected: str) -> None:
		# local_pathが空の場合はEntrypointを基点ノードとする
		via_node = self.fixture.shared_module.entrypoint
		if local_path:
			via_node = self.fixture.get(Reflections).from_fullyname(ModuleDSN.full_joined(self.fixture_module_path, local_path)).node

		full_path = ModuleDSN.local_joined(via_node.full_path, offset_path)
		node = self.fixture.shared_module.entrypoint.whole_by(full_path).as_a(expected_type)
		actual = self.fixture.get(Py2Cpp).transpile(node)
		self.assertEqual(expected, actual)
