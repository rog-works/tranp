import re
from unittest import TestCase

from lark import Token, Tree

from py2cpp.ast.travarsal import ASTFinder, EntryPath
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
		# XXX 参照違反ではあるが、新たなProxyの実装は無駄な手間なので許容する
		return ASTFinder(EntryProxyLark())


class TestEntryPath(TestCase):
	@data_provider([
		('root', 'tree', 0, 'root.tree[0]'),
		('root.tree', 'token', 1, 'root.tree.token[1]'),
		('root.tree[1]', 'token', 2, 'root.tree[1].token[2]'),
	])
	def test_identify(self, origin: str, entry_tag: str, index: int, expected: str) -> None:
		self.assertEqual(EntryPath.identify(origin, entry_tag, index).origin, expected)


	@data_provider([
		('root.tree[1]', 'root.tree'),
		('root.tree.token[1]', 'root.tree.token'),
		('root.tree[1].token[2]', 'root.tree.token'),
		('root.tree.token', 'root.tree.token'),
	])
	def test_de_identify(self, origin: str, expected: str) -> None:
		self.assertEqual(EntryPath(origin).de_identify().origin, expected)


	@data_provider([
		('root.tree[1]', ('root', -1)),
		('root.tree.token[1]', ('root', -1)),
		('tree[1].token[2]', ('tree', 1)),
		('token[2]', ('token', 2)),
	])
	def test_first(self, origin: str, expected: tuple[str, int]) -> None:
		self.assertEqual(EntryPath(origin).first(), expected)


	@data_provider([
		('root.tree[1]', ('tree', 1)),
		('root.tree.token[1]', ('token', 1)),
		('root.tree[1].token[2]', ('token', 2)),
		('root.tree.token', ('token', -1)),
	])
	def test_last(self, origin: str, expected: tuple[str, int]) -> None:
		self.assertEqual(EntryPath(origin).last(), expected)


	@data_provider([
		('tree.tree_a[0].token', r'tree\.tree_a\[0\]\.token'),
	])
	def test_escaped_path(self, origin: str, expected: str) -> None:
		self.assertEqual(EntryPath(origin).escaped_origin, expected)


class TestASTFinder(TestCase):
	@data_provider([
		(Tree('0', []), True),
		(Token('1', ''), False),
		(None, False),
	])
	def test_has_child(self, entry: Entry, expected: bool) -> None:
		finder = Fixture.finder()
		self.assertEqual(finder.has_child(entry), expected)


	@data_provider([
		(Tree('0', []), '0'),
		(Token('1', ''), '1'),
		(None, '__empty__'),
	])
	def test_tag_by(self, entry: Entry, expected: str) -> None:
		finder = Fixture.finder()
		self.assertEqual(finder.tag_by(entry), expected)


	@data_provider([
		('root', True),
		('root.tree_a', True),
		('root.tree_a.__empty__', True),
		('root.tree_a.token_a[1]', True),
		('root.tree_a.tree_b[2]', True),
		('root.tree_a.tree_b[3].token_b', True),
		('root.tree_a.token_a[4]', True),
		('root.tree_a.token_c', True),
		('root.token_d', True),
		('root.outside', False),
		('path.to.unknown', False),
	])
	def test_exists(self, path: str, expected: bool) -> None:
		tree = Fixture.tree()
		finder = Fixture.finder()
		self.assertEqual(finder.exists(tree, path), expected)


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
