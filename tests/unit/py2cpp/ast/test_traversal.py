import re
from unittest import TestCase

from lark import Token, Tree

from py2cpp.ast.travarsal import ASTFinder
from py2cpp.node.nodes import EntryProxyLark
from py2cpp.tp_lark.types import Entry
from tests.test.helper import data_provider

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


	@classmethod
	def finder(cls) -> ASTFinder[Entry]:
		return ASTFinder(EntryProxyLark())


class TestASTFinder(TestCase):
	def test_normalize_tag(self) -> None:
		self.assertEqual(ASTFinder.normalize_tag('tree', 0), 'tree[0]')
		self.assertEqual(ASTFinder.normalize_tag('token', 1), 'token[1]')


	def test_denormalize_tag(self) -> None:
		self.assertEqual(ASTFinder.denormalize_tag('tree[0]'), 'tree')
		self.assertEqual(ASTFinder.denormalize_tag('token[1]'), 'token')
		self.assertEqual(ASTFinder.denormalize_tag('tree'), 'tree')
		self.assertEqual(ASTFinder.denormalize_tag('token'), 'token')


	def test_break_tag(self) -> None:
		self.assertEqual(ASTFinder.break_tag('tree[0]'), ('tree', 0))
		self.assertEqual(ASTFinder.break_tag('token[1]'), ('token', 1))
		self.assertEqual(ASTFinder.break_tag('tree'), ('tree', -1))
		self.assertEqual(ASTFinder.break_tag('token'), ('token', -1))


	def test_escaped_path(self) -> None:
		self.assertEqual(ASTFinder.escaped_path('tree.tree_a[0].token'), r'tree\.tree_a\[0\]\.token')


	@data_provider([
		(Tree('0', []), '0'),
		(Token('1', ''), '1'),
		(None, '__empty__'),
	])
	def test_tag_by(self, entry: Entry, expected: str) -> None:
		finder = Fixture.finder()
		self.assertEqual(finder.tag_by(entry), expected)


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
	def test_pluck(self, path: str, expected: str) -> None:
		tree = Fixture.tree()
		finder = Fixture.finder()
		self.assertEqual(finder.tag_by(finder.pluck(tree, path)), expected)


	@data_provider([
		('root', r'.+\.token_b', ['root.tree_a.tree_b[3].token_b']),
		('root', r'.+\.tree_b\[2\]\.[^.]+', []),
		('root', r'.+\.tree_b\[3\]\.[^.]+', ['root.tree_a.tree_b[3].token_b']),
		('root', r'root\.[^.]+', ['root.tree_a', 'root.token_d']),
	])
	def test_find(self, via: str, pattern: str, expected: list[str]) -> None:
		tree = Fixture.tree()
		finder = Fixture.finder()
		regular = re.compile(pattern)
		tester = lambda _, in_path: regular.fullmatch(in_path) is not None
		entries = finder.find(tree, via, tester)
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
		finder = Fixture.finder()
		entry = finder.pluck(tree, via)
		self.assertEqual(list(finder.full_pathfy(entry, via, depth).keys()), expected)
