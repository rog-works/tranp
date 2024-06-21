from typing import Any
from unittest import TestCase

from rogw.tranp.lang.comment import Comment
from rogw.tranp.test.helper import data_provider


class TestComment(TestCase):
	@data_provider([
		(
			"""Description
line2

Args:
	a (A): A desc
	b (B): B desc
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
	Some example
	```
""",
			{
				'description': 'Description\nline2',
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
				'examples': '```python\nSome example\n```',
			},
		),
		(
			"""Description

Attributes:
	a (A): A desc
	b (B): B desc
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
	])
	def test_comment(self, source: str, expected: dict[str, Any]) -> None:
		comment = Comment.parse(source)
		self.assertEqual(expected['description'], comment.description)
		for index, elem in enumerate(comment.attributes):
			in_expected = expected['attributes'][index]
			self.assertEqual(in_expected['name'], elem.name)
			self.assertEqual(in_expected['type'], elem.type)
			self.assertEqual(in_expected['description'], elem.description)

		for index, elem in enumerate(comment.args):
			in_expected = expected['args'][index]
			self.assertEqual(in_expected['name'], elem.name)
			self.assertEqual(in_expected['type'], elem.type)
			self.assertEqual(in_expected['description'], elem.description)

		self.assertEqual(expected['returns']['type'], comment.returns.type)
		self.assertEqual(expected['returns']['description'], comment.returns.description)

		for index, elem in enumerate(comment.raises):
			in_expected = expected['raises'][index]
			self.assertEqual(in_expected['type'], elem.type)
			self.assertEqual(in_expected['description'], elem.description)

		self.assertEqual(expected['note'], comment.note)
		self.assertEqual(expected['examples'], comment.examples)
