from unittest import TestCase

from rogw.tranp.implements.transpiler.evaluator import LiteralEvaluator
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture


class TestLiteralEvaluator(TestCase):
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
		('file_input.getattr[3]', 1),
		('file_input.getattr[4]', 2),
		('file_input.getattr[5]', 3),
		('file_input.getattr[6]', 6),
	])
	def test_exec_enum_value(self, full_path: str, expected: int | float | str) -> None:
		node = self.fixture.shared_module.entrypoint.whole_by(full_path)
		evaluator = LiteralEvaluator(self.fixture.get(Reflections))
		actual = evaluator.exec(node)
		self.assertEqual(actual, expected)
