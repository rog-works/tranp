from unittest import TestCase

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.implements.semantics.evaluator import LiteralEvaluator
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture


class TestDefinition(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		('1 + 1', 'file_input.sum', 2),
		('1 - 2', 'file_input.sum', -1),
		('-1 + 2', 'file_input.sum', 1),
		('1 - 2.5', 'file_input.sum', -1.5),
		('1.1 * 2', 'file_input.term', 2.2),
		('3 / 2', 'file_input.term', 1.5),
		('3 % 2', 'file_input.term', 1),
		('(10 + 15) * 100 / 50', 'file_input.term', 50.0),
		('"a" + "b" + "c"', 'file_input.sum', '"abc"'),
		("'a' + 'b' + 'c'", 'file_input.sum', "'abc'"),
	])
	def test_exec(self, source_code: str, full_path: str, expected: int | float | str) -> None:
		node = self.fixture.custom_nodes_by(source_code, full_path)
		evaluator = LiteralEvaluator(self.fixture.get(Reflections))
		actual = evaluator.exec(node)
		self.assertEqual(actual, expected)

	@data_provider([
		('file_input.getattr', 0),
	])
	def test_exec_enum(self, full_path: str, expected: int | float | str) -> None:
		node = self.fixture.shared_nodes_by(full_path)
		evaluator = LiteralEvaluator(self.fixture.get(Reflections))
		actual = evaluator.exec(node)
		self.assertEqual(actual, expected)
