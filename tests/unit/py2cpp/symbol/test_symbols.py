from unittest import TestCase

import py2cpp.node.definition as defs
from py2cpp.symbol.symbols import Symbols, Symbolic
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


def _ast(before: str, after: str) -> str:
	aliases = {
		'__main__': 'file_input',
		'A': 'file_input.class_def[2].class_def_raw',
		'A.__init__.params': 'file_input.class_def[2].class_def_raw.block.function_def.function_def_raw.parameters',
		'A.__init__.return': 'file_input.class_def[2].class_def_raw.block.function_def.function_def_raw.return_type',
		'A.__init__.block': 'file_input.class_def[2].class_def_raw.block.function_def.function_def_raw.block',
		'B': 'file_input.class_def[3].class_def_raw',
		'B.B2.block': 'file_input.class_def[3].class_def_raw.block.class_def.class_def_raw.block',
		'B.__init__.params': 'file_input.class_def[3].class_def_raw.block.function_def[1].function_def_raw.parameters',
		'B.__init__.return': 'file_input.class_def[3].class_def_raw.block.function_def[1].function_def_raw.return_type',
		'B.__init__.block': 'file_input.class_def[3].class_def_raw.block.function_def[1].function_def_raw.block',
		'B.func1.params': 'file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.parameters',
		'B.func1.return': 'file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.return_type',
		'B.func1.block': 'file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.block',
	}
	return f'{aliases[before]}.{after}'


def _mod(before: str, after: str) -> str:
	aliases = {
		'xyz': 'tests.unit.py2cpp.symbol.fixtures.test_db_xyz',
		'classes': 'tests.unit.py2cpp.symbol.fixtures.test_db_classes',
	}
	return f'{aliases[before]}.{after}'


class TestSymbols(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		(_ast('__main__', 'import_stmt.import_names.name'), _mod('xyz', 'Z')),
		(_ast('__main__', 'assign_stmt.anno_assign.var'), _mod('classes', 'int')),
		(_ast('__main__', 'assign_stmt.anno_assign.typed_var'), _mod('classes', 'int')),
		(_ast('__main__', 'assign_stmt.anno_assign.number'), _mod('classes', 'int')),
		(_ast('A', 'name'), '__main__.A'),
		(_ast('A.__init__.params', 'paramvalue.typedparam.name'), '__main__.A'),
		(_ast('A.__init__.return', 'typed_none'), _mod('classes', 'None')),
		(_ast('A.__init__.block', 'assign_stmt.anno_assign.getattr'), _mod('classes', 'str')),
		(_ast('A.__init__.block', 'assign_stmt.anno_assign.typed_var'), _mod('classes', 'str')),
		(_ast('A.__init__.block', 'assign_stmt.anno_assign.string'), _mod('classes', 'str')),
		(_ast('B', 'name'), '__main__.B'),
		(_ast('B', 'arguments.argvalue.var'), '__main__.A'),
		(_ast('B.B2.block', 'assign_stmt.anno_assign.var'), _mod('classes', 'str')),
		(_ast('B.B2.block', 'assign_stmt.anno_assign.typed_var'), _mod('classes', 'str')),
		(_ast('B.B2.block', 'assign_stmt.anno_assign.string'), _mod('classes', 'str')),
		(_ast('B.__init__.params', 'paramvalue.typedparam.name'), '__main__.B'),
		(_ast('B.__init__.return', 'typed_none'), _mod('classes', 'None')),
		(_ast('B.__init__.block', 'funccall.getattr.funccall.var'), _mod('classes', 'super')),
		(_ast('B.__init__.block', 'assign_stmt.anno_assign.getattr'), _mod('classes', 'list')),
		(_ast('B.__init__.block', 'assign_stmt.anno_assign.typed_getitem'), _mod('classes', 'list')),
		(_ast('B.__init__.block', 'assign_stmt.anno_assign.list'), _mod('classes', 'list')),
		(_ast('B.func1.params', 'paramvalue[0].typedparam.name'), '__main__.B'),
		(_ast('B.func1.params', 'paramvalue[1].typedparam.name'), _mod('classes', 'list')),
		(_ast('B.func1.return', 'typed_var'), _mod('classes', 'str')),
		(_ast('B.func1.block', 'assign_stmt[0].assign.var'), _mod('classes', 'bool')),
		(_ast('B.func1.block', 'assign_stmt[0].assign.const_false'), _mod('classes', 'bool')),
		(_ast('B.func1.block', 'funccall[1].arguments.argvalue.var'), _mod('classes', 'bool')),
		(_ast('B.func1.block', 'funccall[2].arguments.argvalue.getattr'), _mod('classes', 'list')),
		(_ast('B.func1.block', 'assign_stmt[4].assign.getattr'), _mod('classes', 'str')),
		(_ast('B.func1.block', 'assign_stmt[4].assign.string'), _mod('classes', 'str')),
		(_ast('B.func1.block', 'assign_stmt[5].assign.getattr'), _mod('classes', 'int')),
		(_ast('B.func1.block', 'assign_stmt[5].assign.number'), _mod('classes', 'int')),
		(_ast('B.func1.block', 'return_stmt.getattr'), _mod('classes', 'str')),
	])
	def test_type_of(self, full_path: str, expected: type[defs.ClassType]) -> None:
		resolver = self.fixture.get(Symbols)
		node = self.fixture.shared_nodes.by(full_path).one_of(Symbolic)
		self.assertEqual(resolver.type_of(node).types.domain_id, expected)

	@data_provider([
		(_ast('__main__', 'assign_stmt.anno_assign.number'), _mod('classes', 'int')),
		(_ast('B.func1.block', 'funccall[1].arguments.argvalue.var'), _mod('classes', 'bool')),
		(_ast('B.func1.block', 'funccall[2].arguments.argvalue.getattr'), _mod('classes', 'list')),
		(_ast('B.func1.block', 'funccall[3].arguments.argvalue.getattr'), _mod('classes', 'list')),
	])
	def test_result_of(self, full_path: str, expected: type[defs.ClassType]) -> None:
		resolver = self.fixture.get(Symbols)
		node = self.fixture.shared_nodes.by(full_path)
		self.assertEqual(resolver.result_of(node).types.domain_id, expected)
