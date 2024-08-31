from unittest import TestCase

from rogw.tranp.syntax.ast.path import EntryPath
from rogw.tranp.test.helper import data_provider


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
		('a', 'a'),
		('a.b', r'a\.b'),
		('a.b.c[0]', r'a\.b\.c\[0\]'),
		('a.b[0].c[0]', r'a\.b\[0\]\.c\[0\]'),
	])
	def test_escaped_origin(self, origin: str, expected: str) -> None:
		self.assertEqual(EntryPath(origin).escaped_origin, expected)

	@data_provider([
		('a', 'b', 'a.b'),
		('a', 'b.c', 'a.b.c'),
		('', 'b.c', 'b.c'),
		('', '', ''),
		('a.b', '', 'a.b'),
	])
	def test_joined(self, origin: str, relative: str, expected: str) -> None:
		self.assertEqual(EntryPath(origin).joined(relative), expected)

	@data_provider([
		('a', ('a', -1)),
		('a.b', ('a', -1)),
		('a[0].b.c[1]', ('a', 0)),
		('a[1].b[0].c[0]', ('a', 1)),
	])
	def test_first(self, origin: str, expected: tuple[str, int]) -> None:
		self.assertEqual(EntryPath(origin).first, expected)

	@data_provider([
		('a', ('a', -1)),
		('a.b', ('b', -1)),
		('a[0].b.c[1]', ('c', 1)),
		('a[1].b[0].c.d[2]', ('d', 2)),
	])
	def test_last(self, origin: str, expected: tuple[str, int]) -> None:
		self.assertEqual(EntryPath(origin).last, expected)

	@data_provider([
		('a', 'a'),
		('b.c', 'b'),
		('a[0].b.c[1]', 'a'),
		('c[1].b[0].a[0]', 'c'),
	])
	def test_first_tag(self, origin: str, expected: str) -> None:
		self.assertEqual(EntryPath(origin).first_tag, expected)

	@data_provider([
		('a', 'a'),
		('b.c', 'c'),
		('a[0].b.c[1]', 'c'),
		('c[1].b[0].a[0]', 'a'),
	])
	def test_last_tag(self, origin: str, expected: str) -> None:
		self.assertEqual(EntryPath(origin).last_tag, expected)

	@data_provider([
		('b.c', 'b'),
		('a[0].b.c[1]', 'b'),
		('c[1].b[0].a[0]', 'b'),
	])
	def test_parent_tag(self, origin: str, expected: str) -> None:
		self.assertEqual(EntryPath(origin).parent_tag, expected)

	@data_provider([
		('a', 'a', True),
		('a', 'b', False),
		('b.c', 'c', True),
		('a[0].b.c[1]', 'c', True),
		('a[0].b.c[1]', 'b', True),
		('a[0].b.c[1]', 'a', True),
		('a[0].b.c[1]', '1', False),
	])
	def test_contains(self, origin: str, entry_tag: str, expected: bool) -> None:
		self.assertEqual(EntryPath(origin).contains(entry_tag), expected)

	@data_provider([
		('a', ['a'], True),
		('a', ['b'], False),
		('b.c', ['c'], False),
		('a[0].b.c[1]', ['a'], False),
		('a[0].b.c[1]', ['a', 'b', 'c'], True),
		('a[0].b.c[1]', ['1'], False),
	])
	def test_consists_of_only(self, origin: str, entry_tags: list[str], expected: bool) -> None:
		self.assertEqual(EntryPath(origin).consists_of_only(*entry_tags), expected)

	@data_provider([
		('a', 'a'),
		('b.c', 'b.c'),
		('a[0].b.c[1]', 'a.b.c'),
		('c[1].b[0].a[0]', 'c.b.a'),
	])
	def test_de_identify(self, origin: str, expected: bool) -> None:
		self.assertEqual(EntryPath(origin).de_identify().origin, expected)

	@data_provider([
		('b.c', 'b', 'c'),
		('a[0].b.c[1]', 'a[0]', 'b.c[1]'),
		('c[1].b[0].a[0]', 'c[1].b[0]', 'a[0]'),
	])
	def test_relativefy(self, origin: str, starts: str, expected: bool) -> None:
		self.assertEqual(EntryPath(origin).relativefy(starts).origin, expected)

	@data_provider([
		('b.c', 1, 'c'),
		('b.c', -1, 'b'),
		('b.c', 2, ''),
		('b.c', 0, 'b.c'),
		('a[0].b.c[1]', 1, 'b.c[1]'),
		('a[0].b.c[1]', -2, 'a[0]'),
		('c[1].b[0].a[0]', 2, 'a[0]'),
		('c[1].b[0].a[0]', -3, ''),
	])
	def test_shift(self, origin: str, skip: int, expected: bool) -> None:
		self.assertEqual(EntryPath(origin).shift(skip).origin, expected)
