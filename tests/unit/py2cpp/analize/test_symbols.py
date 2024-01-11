from typing import cast
from unittest import TestCase

from py2cpp.analize.db import SymbolRaw
from py2cpp.analize.symbols import Primitives, Symbols, Symbolic
from py2cpp.ast.dsn import DSN
import py2cpp.node.definition as defs
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


def _ast(before: str, after: str) -> str:
	aliases = {
		'__main__': 'file_input',
		'A': 'file_input.class_def[2]',
		'A.__init__.params': 'file_input.class_def[2].class_def_raw.block.function_def.function_def_raw.parameters',
		'A.__init__.return': 'file_input.class_def[2].class_def_raw.block.function_def.function_def_raw.return_type',
		'A.__init__.block': 'file_input.class_def[2].class_def_raw.block.function_def.function_def_raw.block',
		'B': 'file_input.class_def[3]',
		'B.B2': 'file_input.class_def[3].class_def_raw.block.class_def',
		'B.B2.block': 'file_input.class_def[3].class_def_raw.block.class_def.class_def_raw.block',
		'B.B2.class_func': 'file_input.class_def[3].class_def_raw.block.class_def.class_def_raw.block.function_def',
		'B.B2.class_func.params': 'file_input.class_def[3].class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.parameters',
		'B.B2.class_func.return': 'file_input.class_def[3].class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.return_type',
		'B.B2.class_func.block': 'file_input.class_def[3].class_def_raw.block.class_def.class_def_raw.block.function_def.function_def_raw.block',
		'B.__init__.params': 'file_input.class_def[3].class_def_raw.block.function_def[1].function_def_raw.parameters',
		'B.__init__.return': 'file_input.class_def[3].class_def_raw.block.function_def[1].function_def_raw.return_type',
		'B.__init__.block': 'file_input.class_def[3].class_def_raw.block.function_def[1].function_def_raw.block',
		'B.func1.params': 'file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.parameters',
		'B.func1.return': 'file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.return_type',
		'B.func1.block': 'file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.block',
	}
	return DSN.join(aliases[before], after)


def _mod(before: str, after: str) -> str:
	aliases = {
		'xyz': 'tests.unit.py2cpp.analize.fixtures.test_db_xyz',
		'classes': 'tests.unit.py2cpp.analize.fixtures.test_db_classes',
	}
	return DSN.join(aliases[before], after)


class TestSymbols(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		(int, _mod('classes', 'int')),
		(str, _mod('classes', 'str')),
		(bool, _mod('classes', 'bool')),
		(tuple, _mod('classes', 'tuple')),
		(list, _mod('classes', 'list')),
		(dict, _mod('classes', 'dict')),
		(None, _mod('classes', 'None')),
	])
	def test_type_of_primitive(self, primitive_type: type[Primitives], expected: str) -> None:
		symbols = self.fixture.get(Symbols)
		self.assertEqual(symbols.type_of_primitive(primitive_type).types.domain_id, expected)

	@data_provider([
		(_mod('classes', 'Unknown'),),
	])
	def test_type_of_unknown(self, expected: str) -> None:
		symbols = self.fixture.get(Symbols)
		self.assertEqual(symbols.type_of_unknown().types.domain_id, expected)

	@data_provider([
		(_ast('__main__', 'import_stmt.import_names.name'), _mod('xyz', 'Z'), []),
		(_ast('__main__', 'assign_stmt[1].anno_assign.var'), _mod('classes', 'int'), []),
		(_ast('__main__', 'assign_stmt[1].anno_assign.typed_var'), _mod('classes', 'int'), []),
		(_ast('__main__', 'assign_stmt[1].anno_assign.number'), _mod('classes', 'int'), []),
		(_ast('__main__', 'assign_stmt[4].assign.var'), _mod('classes', 'dict'), [_mod('classes', 'str'), _mod('classes', 'int')]),
		(_ast('A', ''), '__main__.A', []),
		(_ast('A', 'class_def_raw.name'), '__main__.A', []),
		(_ast('A.__init__.params', 'paramvalue.typedparam.name'), '__main__.A', []),
		(_ast('A.__init__.return', 'typed_none'), _mod('classes', 'None'), []),
		(_ast('A.__init__.block', 'assign_stmt.anno_assign.getattr'), _mod('classes', 'str'), []),
		(_ast('A.__init__.block', 'assign_stmt.anno_assign.typed_var'), _mod('classes', 'str'), []),
		(_ast('A.__init__.block', 'assign_stmt.anno_assign.string'), _mod('classes', 'str'), []),
		(_ast('B', ''), '__main__.B', []),
		(_ast('B', 'class_def_raw.name'), '__main__.B', []),
		(_ast('B', 'class_def_raw.typed_arguments.typed_argvalue.typed_var'), '__main__.A', []),
		(_ast('B.B2', ''), '__main__.B.B2', []),
		(_ast('B.B2.block', 'assign_stmt.anno_assign.var'), _mod('classes', 'str'), []),
		(_ast('B.B2.block', 'assign_stmt.anno_assign.typed_var'), _mod('classes', 'str'), []),
		(_ast('B.B2.block', 'assign_stmt.anno_assign.string'), _mod('classes', 'str'), []),
		(_ast('B.B2.class_func', ''), '__main__.B.B2.class_func', []),
		(_ast('B.B2.class_func.params', 'paramvalue.typedparam.name'), '__main__.B.B2', []),
		(_ast('B.B2.class_func.return', 'typed_getitem'), _mod('classes', 'dict'), [_mod('classes', 'str'), _mod('classes', 'int')]),
		(_ast('B.B2.class_func.block', 'return_stmt.dict'), _mod('classes', 'dict'), [_mod('classes', 'str'), _mod('classes', 'int')]),
		(_ast('B.__init__.params', 'paramvalue.typedparam.name'), '__main__.B', []),
		(_ast('B.__init__.return', 'typed_none'), _mod('classes', 'None'), []),
		(_ast('B.__init__.block', 'funccall'), '__main__.A', []),
		(_ast('B.__init__.block', 'funccall.getattr.funccall.var'), _mod('classes', 'super'), []),
		(_ast('B.__init__.block', 'assign_stmt'), _mod('classes', 'list'), [_mod('classes', 'int')]),
		(_ast('B.__init__.block', 'assign_stmt.anno_assign.getattr'), _mod('classes', 'list'), [_mod('classes', 'int')]),
		(_ast('B.__init__.block', 'assign_stmt.anno_assign.typed_getitem'), _mod('classes', 'list'), [_mod('classes', 'int')]),
		(_ast('B.__init__.block', 'assign_stmt.anno_assign.list'), _mod('classes', 'list'), [_mod('classes', 'Unknown')]),
		(_ast('B.func1.params', 'paramvalue[0].typedparam.name'), '__main__.B', []),
		(_ast('B.func1.params', 'paramvalue[1].typedparam.name'), _mod('classes', 'list'), ['__main__.B']),
		(_ast('B.func1.return', 'typed_var'), _mod('classes', 'str'), []),
		(_ast('B.func1.block', 'assign_stmt[0].assign.var'), _mod('classes', 'bool'), []),
		(_ast('B.func1.block', 'assign_stmt[0].assign.const_false'), _mod('classes', 'bool'), []),
		(_ast('B.func1.block', 'funccall[1].arguments.argvalue.var'), _mod('classes', 'bool'), []),
		(_ast('B.func1.block', 'funccall[2].arguments.argvalue.getattr'), _mod('classes', 'list'), [_mod('classes', 'int')]),
		(_ast('B.func1.block', 'funccall[3].arguments.argvalue.getattr'), _mod('classes', 'list'), [_mod('classes', 'int')]),
		(_ast('B.func1.block', 'assign_stmt[4].assign.getattr'), _mod('classes', 'str'), []),
		(_ast('B.func1.block', 'assign_stmt[4].assign.string'), _mod('classes', 'str'), []),
		(_ast('B.func1.block', 'assign_stmt[5].assign.getattr'), _mod('classes', 'int'), []),
		(_ast('B.func1.block', 'assign_stmt[5].assign.number'), _mod('classes', 'int'), []),
		(_ast('B.func1.block', 'return_stmt.getattr'), _mod('classes', 'str'), []),
	])
	def test_type_of(self, full_path: str, expected: str, attrs_expected: list[str]) -> None:
		symbols = self.fixture.get(Symbols)
		node = self.fixture.shared_nodes.by(full_path)
		symbol = symbols.type_of(node)
		self.assertEqual(symbol.types.domain_id, expected)
		self.assertEqual(len(symbol.attrs), len(attrs_expected))
		for index, in_expected in enumerate(attrs_expected):
			self.assertEqual(symbol.attrs[index].types.domain_id, in_expected)
