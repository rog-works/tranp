from typing import Any, TypedDict
from unittest import TestCase

from lark import Token, Tree

from py2cpp.node.serializer import serialize
from py2cpp.tp_lark.entry import Entry, EntryOfLark

from tests.test.fixture import Fixture
from tests.test.helper import data_provider

T_Sum = TypedDict('T_Sum', {'left': str, 'operator': str, 'right': str})
T_FileInput = TypedDict('T_FileInput', {'statements': list[T_Sum]})


class TestSerializer(TestCase):
	fixture = Fixture.make(__file__)

	@data_provider([
		(
			EntryOfLark(Tree(Token('RULE', 'file_input'), [
				Tree(Token('RULE', 'sum'), [
					Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '1')]),
					Token('PLUS', '+'),
					Tree(Token('RULE', 'number'), [Token('DEC_NUMBER', '2')])
				]),
			])),
			'file_input',
			{'statements': [{'left': '1', 'operator': '+', 'right': '2'}]},
		),
	])
	def test_serialize(self, tree: Entry, full_path: str, expected: dict[str, Any]) -> None:
		node = self.fixture.custom_nodes(tree).by(full_path)
		dump = serialize(node, T_FileInput)
		self.assertEqual(dump, expected)
