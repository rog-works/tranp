import re
from unittest import TestCase

from lark import Token, Tree

from tests.test.helper import data_provider
from py2cpp.tp_lark.travarsal import (
	break_tag,
	denormalize_tag,
	escaped_path,
	find_entries,
	full_pathfy,
	normalize_tag,
	pluck_entry,
	tag_by_entry,
)
from py2cpp.tp_lark.types import Entry

class Fixture:
	@classmethod
	def tree(cls) -> Tree:
		return Tree('root', [
			Tree('tree_a', [
				None,
				Token('token_a', ''),
				Tree('tree_b', []),
				Tree('tree_b', [
					Token('token_b', ''),
				]),
				Token('token_a', ''),
				Token('token_c', ''),
			]),
			Token('token_d', ''),
		])


class TestTraversal(TestCase):
	def test_normalize_tag(self) -> None:
		self.assertEqual(normalize_tag('tree', 0), 'tree[0]')
		self.assertEqual(normalize_tag('token', 1), 'token[1]')


	def test_denormalize_tag(self) -> None:
		self.assertEqual(denormalize_tag('tree[0]'), 'tree')
		self.assertEqual(denormalize_tag('token[1]'), 'token')
		self.assertEqual(denormalize_tag('tree'), 'tree')
		self.assertEqual(denormalize_tag('token'), 'token')


	def test_break_tag(self) -> None:
		self.assertEqual(break_tag('tree[0]'), ('tree', 0))
		self.assertEqual(break_tag('token[1]'), ('token', 1))
		self.assertEqual(break_tag('tree'), ('tree', -1))
		self.assertEqual(break_tag('token'), ('token', -1))


	def test_escaped_path(self) -> None:
		self.assertEqual(escaped_path('tree.tree_a[0].token'), r'tree\.tree_a\[0\]\.token')


	@data_provider([
		(Tree('0', []), '0'),
		(Token('1', ''), '1'),
		(None, '__empty__'),
	])
	def test_tag_by_entry(self, entry: Entry, expected: str) -> None:
		self.assertEqual(tag_by_entry(entry), expected)


	@data_provider([
		('root', 'root'),
		('root.tree_a', 'tree_a'),
		('root.tree_a.__empty__', '__empty__'),
		('root.tree_a.token_a[1]', 'token_a'),
		('root.tree_a.tree_b[2]', 'tree_b'),
		('root.tree_a.tree_b[3].token_b', 'token_b'),
		('root.tree_a.token_a[4]', 'token_a'),
		('root.tree_a.token_c', 'token_c'),
		('root.token_d', 'token_d'),
	])
	def test_pluck_entry(self, path: str, expected: str) -> None:
		tree = Fixture.tree()
		self.assertEqual(tag_by_entry(pluck_entry(tree, path)), expected)


	@data_provider([
		('root', r'.+\.token_b', ['root.tree_a.tree_b[3].token_b']),
		('root', r'.+\.tree_b\[2\]\.[^.]+', []),
		('root', r'.+\.tree_b\[3\]\.[^.]+', ['root.tree_a.tree_b[3].token_b']),
		('root', r'root\.[^.]+', ['root.tree_a', 'root.token_d']),
	])
	def test_find_entries(self, via: str, pattern: str, expected: list[str]) -> None:
		tree = Fixture.tree()
		regular = re.compile(pattern)
		tester = lambda _, in_path: regular.fullmatch(in_path) is not None
		entries = find_entries(tree, via, tester)
		self.assertEqual(list(entries.keys()), expected)


	@data_provider([
		('root.tree_a', -1, [
			'root.tree_a',
			'root.tree_a.__empty__',
			'root.tree_a.token_a[1]',
			'root.tree_a.tree_b[2]',
			'root.tree_a.tree_b[3]',
			'root.tree_a.tree_b[3].token_b',
			'root.tree_a.token_a[4]',
			'root.tree_a.token_c',
		]),
		('root.tree_a.tree_b[3]', -1, ['root.tree_a.tree_b[3]', 'root.tree_a.tree_b[3].token_b']),
		('root.tree_a.tree_b[3].token_b', -1, ['root.tree_a.tree_b[3].token_b']),
		('root.token_d', -1, ['root.token_d']),
		('root.tree_a', 1, [
			'root.tree_a',
			'root.tree_a.__empty__',
			'root.tree_a.token_a[1]',
			'root.tree_a.tree_b[2]',
			'root.tree_a.tree_b[3]',
			'root.tree_a.token_a[4]',
			'root.tree_a.token_c',
		]),
		('root', 1, ['root', 'root.tree_a', 'root.token_d']),
	])
	def test_full_pathfy(self, via: str, depth: int, expected: list[str]) -> None:
		tree = Fixture.tree()
		entry = pluck_entry(tree, via)
		self.assertEqual(list(full_pathfy(entry, via, depth).keys()), expected)
