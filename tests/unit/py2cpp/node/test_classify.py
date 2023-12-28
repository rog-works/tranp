from unittest import TestCase

from py2cpp.node.classify import Classify
import py2cpp.node.definition as defs
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


def by(before: str, after: str) -> str:
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


class TestClassify(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		(by('__main__', 'import_stmt.import_names.name'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_xyz.Z'),
		(by('__main__', 'assign_stmt.anno_assign.var'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.int'),
		(by('A', 'name'), '__main__.A'),
		(by('A.__init__.params', 'paramvalue.typedparam.name'), '__main__.A'),
		(by('A.__init__.return', 'typed_none'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.None'),
		(by('A.__init__.block', 'assign_stmt.anno_assign.getattr'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str'),
		(by('B', 'name'), '__main__.B'),
		(by('B', 'arguments.argvalue.var'), '__main__.A'),
		(by('B.B2.block', 'assign_stmt.anno_assign.var'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str'),
		(by('B.__init__.params', 'paramvalue.typedparam.name'), '__main__.B'),
		(by('B.__init__.return', 'typed_none'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.None'),
		(by('B.__init__.block', 'funccall.getattr.funccall.var'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.super'),
		(by('B.__init__.block', 'assign_stmt.anno_assign.getattr'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.list'),
		(by('B.func1.params', 'paramvalue[0].typedparam.name'), '__main__.B'),
		(by('B.func1.params', 'paramvalue[1].typedparam.name'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.list'),
		(by('B.func1.return', 'typed_var'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str'),
		(by('B.func1.block', 'assign_stmt[0].assign.var'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.Unknown'),
		(by('B.func1.block', 'assign_stmt[0].assign.const_false'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.bool'),
		(by('B.func1.block', 'funccall[1].arguments.argvalue.var'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.Unknown'),
		(by('B.func1.block', 'funccall[2].arguments.argvalue.getattr'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.list'),
		(by('B.func1.block', 'assign_stmt[4].assign.getattr'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str'),
		(by('B.func1.block', 'assign_stmt[4].assign.string'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str'),
		(by('B.func1.block', 'assign_stmt[5].assign.getattr'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.int'),
		(by('B.func1.block', 'assign_stmt[5].assign.number'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.int'),
		(by('B.func1.block', 'return_stmt.getattr'), 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str'),
	])
	def test_type_of(self, full_path: str, expected: type[defs.Types]) -> None:
		classify = self.fixture.get(Classify)
		node = self.fixture.shared_nodes.by(full_path).one_of(defs.Symbol | defs.GenericType | defs.Literal | defs.Types)
		self.assertEqual(classify.type_of(node).domain_id, expected)
