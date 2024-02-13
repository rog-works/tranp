import re
from unittest import TestCase

from lark import Token, Tree

from rogw.tranp.ast.entry import Entry
from rogw.tranp.ast.finder import ASTFinder
from rogw.tranp.tp_lark.entry import EntryOfLark
from tests.test.helper import data_provider

class Fixture:
	@classmethod
	def tree(cls) -> Entry:
		tree = Tree('root', [
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
		return EntryOfLark(tree)

	@classmethod
	def finder(cls) -> ASTFinder:
		return ASTFinder()


class TestASTFinder(TestCase):
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
		self.assertEqual(finder.pluck(tree, path).name, expected)

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
