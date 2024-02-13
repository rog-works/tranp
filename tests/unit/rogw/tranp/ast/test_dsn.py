from unittest import TestCase

from rogw.tranp.ast.dsn import DSN
from tests.test.helper import data_provider


class TestDSN(TestCase):
	@data_provider([
		('a.b.c', 3),
		('a.c', 2),
		('a.b', 2),
		('.b.c', 2),
		('a', 1),
	])
	def test_elem_counts(self, origin: str, expected: int) -> None:
		self.assertEqual(DSN.elem_counts(origin), expected)

	@data_provider([
		('a.b.c', ['a', 'b', 'c']),
		('a..c', ['a', 'c']),
		('a.b', ['a', 'b']),
		('.b.c', ['b', 'c']),
		('a', ['a']),
		('a.', ['a']),
		('', []),
	])
	def test_elements(self, origin: str, expected: list[str]) -> None:
		self.assertEqual(DSN.elements(origin), expected)

	@data_provider([
		(['a', 'b', 'c'], 'a.b.c'),
		(['a', '', 'c'], 'a.c'),
		(['a', 'b', ''], 'a.b'),
		(['', 'b', 'c'], 'b.c'),
		(['a', None], 'a'),
	])
	def test_join(self, elems: list[str], expected: str) -> None:
		self.assertEqual(DSN.join(*elems), expected)

	@data_provider([
		('a.b.c', 2, 'a.b'),
		('a.b.c', 4, 'a.b.c'),
		('a.c', 1, 'a'),
		('a.b', 2, 'a.b'),
		('.b.c', 2, 'b.c'),
		('.b.c', 1, 'b'),
	])
	def test_left(self, origin: str, counts: int, expected: str) -> None:
		self.assertEqual(DSN.left(origin, counts), expected)

	@data_provider([
		('a.b.c', 2, 'b.c'),
		('a.b.c', 4, 'a.b.c'),
		('a.c', 1, 'c'),
		('a.b', 2, 'a.b'),
		('.b.c', 2, 'b.c'),
		('.b.c', 3, 'b.c'),
	])
	def test_right(self, origin: str, counts: int, expected: str) -> None:
		self.assertEqual(DSN.right(origin, counts), expected)

	@data_provider([
		('a.b.c', 'a'),
		('a.b.c', 'a'),
		('b.c', 'b'),
		('c.b', 'c'),
		('.a.b', 'a'),
		('a.b.', 'a'),
	])
	def test_root(self, origin: str, expected: str) -> None:
		self.assertEqual(DSN.root(origin), expected)

	@data_provider([
		('a.b.c', 'b'),
		('a.b.c', 'b'),
		('b.c', 'b'),
		('c.b', 'c'),
		('.a.b', 'a'),
		('a.b.', 'a'),
	])
	def test_parent(self, origin: str, expected: str) -> None:
		self.assertEqual(DSN.parent(origin), expected)
