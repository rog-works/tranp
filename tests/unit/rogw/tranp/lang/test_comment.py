from typing import Any
from unittest import TestCase

from rogw.tranp.lang.comment import Comment
from rogw.tranp.test.helper import data_provider


class TestComment(TestCase):
	@data_provider([
		(
			"""Description

				* 1
					* 1-1
			Args:
				a: A desc
				b: B desc
			Returns:
				R: R desc
			Raises:
				E1: E1 desc
				E2: E2 desc
			Note:
				Some note
				line2
			Examples:
				```python
				def example() -> None:
					...
				```
			""",
			{
				'description': 'Description\n\n* 1\n\t* 1-1',
				'attributes': [],
				'args': [
					{'name': 'a', 'type': 'A', 'description': 'A desc'},
					{'name': 'b', 'type': 'B', 'description': 'B desc'},
				],
				'returns': {'type': 'R', 'description': 'R desc'},
				'raises': [
					{'type': 'E1', 'description': 'E1 desc'},
					{'type': 'E2', 'description': 'E2 desc'},
				],
				'note': 'Some note\nline2',
				'examples': '```python\ndef example() -> None:\n\t...\n```',
			},
		),
		(
			"""Description

			Attributes:
				a: A desc
				b: B desc
			""",
			{
				'description': 'Description',
				'attributes': [
					{'name': 'a', 'type': 'A', 'description': 'A desc'},
					{'name': 'b', 'type': 'B', 'description': 'B desc'},
				],
				'args': [],
				'returns': {'type': '', 'description': ''},
				'raises': [],
				'note': '',
				'examples': '',
			},
		),
		(
			"""Description

			Args:
				a: A desc
				b: B desc
			Returns:
				desc
			""",
			{
				'description': 'Description',
				'attributes': [],
				'args': [
					{'name': 'a', 'type': 'A', 'description': 'A desc'},
					{'name': 'b', 'type': '', 'description': 'B desc'},
				],
				'returns': {'type': '', 'description': 'desc'},
				'raises': [],
				'note': '',
				'examples': '',
			},
		),
	])
	def test_parse(self, source: str, expected: dict[str, Any]) -> None:
		comment = Comment.parse(source)
		self.assertEqual(comment.description, expected['description'])
		for index, elem in enumerate(comment.attributes):
			in_expected = expected['attributes'][index]
			self.assertEqual(elem.name, in_expected['name'])
			self.assertEqual(elem.type, in_expected['type'])
			self.assertEqual(elem.description, in_expected['description'])

		for index, elem in enumerate(comment.args):
			in_expected = expected['args'][index]
			self.assertEqual(elem.name, in_expected['name'])
			self.assertEqual(elem.type, in_expected['type'])
			self.assertEqual(elem.description, in_expected['description'])

		self.assertEqual(comment.returns.type, expected['returns']['type'])
		self.assertEqual(comment.returns.description, expected['returns']['description'])

		for index, elem in enumerate(comment.raises):
			in_expected = expected['raises'][index]
			self.assertEqual(elem.type, in_expected['type'])
			self.assertEqual(elem.description, in_expected['description'])

		self.assertEqual(comment.note, expected['note'])
		self.assertEqual(comment.examples, expected['examples'])
