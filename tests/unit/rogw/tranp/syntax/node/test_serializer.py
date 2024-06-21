from typing import Any, TypedDict
from unittest import TestCase

from rogw.tranp.syntax.node.serializer import serialize
from rogw.tranp.test.helper import data_provider
from tests.test.fixture import Fixture

T_Sum = TypedDict('T_Sum', {'elements': list[str]})
T_FileInput = TypedDict('T_FileInput', {'statements': list[T_Sum]})


class TestSerializer(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		(
			'1 + 2',
			'file_input',
			{'statements': [{'elements': ['1', '+', '2']}]},
		),
	])
	def test_serialize(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes_by(source, full_path)
		dump = serialize(node, T_FileInput)
		self.assertEqual(expected, dump)
