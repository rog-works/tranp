import os
import re
from unittest import TestCase

from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.i18n.i18n import I18n
from rogw.tranp.implements.cpp.providers.semantics import cpp_plugin_provider
from rogw.tranp.implements.cpp.transpiler.py2cpp import Py2Cpp
from rogw.tranp.lang.module import fullyname
from rogw.tranp.semantics.errors import NotSupportedError, ProcessingError, UnresolvedSymbolError
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.test.helper import data_provider
from rogw.tranp.transpiler.types import TranspilerOptions
from rogw.tranp.view.render import Renderer
from tests.test.fixture import Fixture


class ASTMapping:
	_InvalidOps = f'file_input.class_def'

	aliases = {
		'InvalidOps.tenary_to_union_types.block': f'{_InvalidOps}.class_def_raw.block.function_def[0].function_def_raw.block',
		'InvalidOps.param_of_raw_or_null': f'{_InvalidOps}.class_def_raw.block.function_def[1]',
		'InvalidOps.return_of_raw_or_null': f'{_InvalidOps}.class_def_raw.block.function_def[2]',
		'InvalidOps.yield_return.block': f'{_InvalidOps}.class_def_raw.block.function_def[3].function_def_raw.block',
		'InvalidOps.delete_relay.block': f'{_InvalidOps}.class_def_raw.block.function_def[4].function_def_raw.block',
		'InvalidOps.destruction_assign.block': f'{_InvalidOps}.class_def_raw.block.function_def[5].function_def_raw.block',
	}


def _ast(before: str, after: str) -> str:
	return ModuleDSN.local_joined(ASTMapping.aliases[before], after)


def make_renderer(i18n: I18n) -> Renderer:
	return Renderer([os.path.join(tranp_dir(), 'data/cpp/template')], i18n.t)


class TestPy2CppError(TestCase):
	fixture = Fixture.make(__file__, {
		fullyname(Py2Cpp): Py2Cpp,
		fullyname(PluginProvider): cpp_plugin_provider,
		fullyname(TranspilerOptions): lambda: TranspilerOptions(verbose=False),
		fullyname(Renderer): make_renderer,
	})

	@data_provider([
		(_ast('InvalidOps.tenary_to_union_types.block', 'assign'), UnresolvedSymbolError, r'Only Nullable.'),
		(_ast('InvalidOps.param_of_raw_or_null', ''), ProcessingError, r'Unexpected UnionType.'),
		(_ast('InvalidOps.return_of_raw_or_null', ''), ProcessingError, r'Unexpected UnionType.'),
		(_ast('InvalidOps.yield_return.block', 'yield_stmt'), NotSupportedError, r'Denied yield return.'),
		(_ast('InvalidOps.delete_relay.block', 'del_stmt'), ProcessingError, r'Unexpected delete target.'),
		(_ast('InvalidOps.destruction_assign.block', 'assign'), ProcessingError, r'Not allowed destruction assign.'),
	])
	def test_exec_error(self, full_path: str, expected_error: type[Exception], expected: re.Pattern) -> None:
		transpiler = self.fixture.get(Py2Cpp)
		node = self.fixture.shared_nodes_by(full_path)
		with self.assertRaisesRegex(expected_error, expected):
			transpiler.transpile(node)
