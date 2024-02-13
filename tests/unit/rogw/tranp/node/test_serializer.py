from typing import Any, TypedDict
from unittest import TestCase

from rogw.tranp.node.serializer import serialize

from tests.test.fixture import Fixture
from tests.test.helper import data_provider

T_Sum = TypedDict('T_Sum', {'left': str, 'operator': str, 'right': list[str]})
T_FileInput = TypedDict('T_FileInput', {'statements': list[T_Sum]})


class TestSerializer(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		(
			'1 + 2',
			'file_input',
			{'statements': [{'left': '1', 'operator': '+', 'right': ['2']}]},
		),
	])
	def test_serialize(self, source: str, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(source).by(full_path)
		dump = serialize(node, T_FileInput)
		self.assertEqual(dump, expected)
