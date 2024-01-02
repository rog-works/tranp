from unittest import TestCase

from py2cpp.ast.dsn import DSN
from tests.test.helper import data_provider


class TestDSN(TestCase):
	@data_provider([
		('a.b.c', 3),
		('a.c', 2),
		('a.b', 2),
		('.b.c', 3),
		('a', 1),
	])
	def test_elem_counts(self, origin: str, expected: int) -> None:
		self.assertEqual(DSN.elem_counts(origin), expected)

	@data_provider([
		(['a', 'b', 'c'], 'a.b.c'),
		(['a', '', 'c'], 'a.c'),
		(['a', 'b', ''], 'a.b'),
		(['', 'b', 'c'], '.b.c'),
		(['a', None], 'a'),
	])
	def test_join(self, elems: list[str], expected: str) -> None:
		self.assertEqual(DSN.join(*elems), expected)

	@data_provider([
		('a.b.c', 2, 'a.b'),
		('a.b.c', 4, 'a.b.c'),
		('a.c', 1, 'a'),
		('a.b', 2, 'a.b'),
		('.b.c', 2, '.b'),
		('.b.c', 1, ''),
	])
	def test_left(self, origin: str, counts: int, expected: str) -> None:
		self.assertEqual(DSN.left(origin, counts), expected)

	@data_provider([
		('a.b.c', 2, 'b.c'),
		('a.b.c', 4, 'a.b.c'),
		('a.c', 1, 'c'),
		('a.b', 2, 'a.b'),
		('.b.c', 2, 'b.c'),
		('.b.c', 1, 'c'),
	])
	def test_right(self, origin: str, counts: int, expected: str) -> None:
		self.assertEqual(DSN.right(origin, counts), expected)
