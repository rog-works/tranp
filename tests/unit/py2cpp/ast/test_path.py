from unittest import TestCase

from py2cpp.ast.path import EntryPath
from tests.test.helper import data_provider


class TestEntryPath(TestCase):
	@data_provider([
		(['a', 'b'], 'a.b'),
		(['a', 'b.c'], 'a.b.c'),
		(['', 'b.c'], 'b.c'),
		(['', ''], ''),
		(['a.b', ''], 'a.b'),
	])
	def test_join(self, elems: list[str], expected: str) -> None:
		self.assertEqual(EntryPath.join(*elems).origin, expected)

	@data_provider([
		('a.b', 'c', 0, 'a.b.c[0]'),
		('a.b.c', 'd', 1, 'a.b.c.d[1]'),
		('b.c', 'd', 0, 'b.c.d[0]'),
	])
	def test_identify(self, origin: str, entry_tag: str, index: int, expected: str) -> None:
		self.assertEqual(EntryPath.identify(origin, entry_tag, index).origin, expected)

	@data_provider([
		('a.b', True),
		('a.b.c', True),
		('b.c', True),
		('', False),
		('.', False),
	])
	def test_valid(self, origin: str, expected: bool) -> None:
		self.assertEqual(EntryPath(origin).valid, expected)

	@data_provider([
		('a.b', ['a', 'b']),
		('a.b.c', ['a', 'b', 'c']),
		('b.c', ['b', 'c']),
		('', []),
		('.', []),
	])
	def test_elements(self, origin: str, expected: list[str]) -> None:
		self.assertEqual(EntryPath(origin).elements, expected)

	@data_provider([
		('a', 'b', 'a.b'),
		('a', 'b.c', 'a.b.c'),
		('', 'b.c', 'b.c'),
		('', '', ''),
		('a.b', '', 'a.b'),
	])
	def test_joined(self, origin: str, relative: str, expected: str) -> None:
		self.assertEqual(EntryPath(origin).joined(relative), expected)
