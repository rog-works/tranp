from unittest import TestCase

from py2cpp.node.classify import Classify
import py2cpp.node.definition as defs
from tests.test.fixture import Fixture
from tests.test.helper import data_provider


class TestClassify(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		('file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[0].assign.var', 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.Unknown'),
		('file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[0].assign.const_false', 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.bool'),
		('file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[5].assign.getattr', 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.int'),
		('file_input.class_def[3].class_def_raw.block.function_def[2].function_def_raw.block.assign_stmt[4].assign.getattr', 'tests.unit.py2cpp.node.fixtures.test_symboldb_classes.str'),
	])
	def test_type_of(self, full_path: str, expected: type[defs.Types]) -> None:
		classify = self.fixture.get(Classify)
		node = self.fixture.shared_nodes.by(full_path).one_of(defs.Symbol | defs.GenericType | defs.Literal | defs.Types)
		self.assertEqual(classify.type_of(node).domain_id, expected)
