from typing import cast
from unittest import TestCase

from lark import Token, Tree

from py2cpp.ast.cache import EntryCache


class TestEntryCache(TestCase):
	def test_exists(self) -> None:
		cache = EntryCache()
		cache.add('root', Tree('root', []))
		self.assertEqual(cache.exists('root'), True)

	def test_by(self) -> None:
		cache = EntryCache()
		root = Tree('root', [])
		cache.add('root', root)
		self.assertEqual(cache.by('root'), root)

	def test_group_by(self) -> None:
		cache = EntryCache()
		root = Tree('root', [
			Token('term_a', ''),
			Tree('tree_a', [
				Token('term_b', ''),
			]),
			Token('term_c', ''),
		])
		tree_a = cast(Tree, root.children[1])
		cache.add('root', root)
		cache.add('root.term_a', root.children[0])
		cache.add('root.tree_a', root.children[1])
		cache.add('root.tree_a.term_b', tree_a.children[0])
		cache.add('root.term_c', root.children[2])
		arr = list(cache.group_by('root').values())
		self.assertEqual(arr, [root, root.children[0], tree_a, tree_a.children[0], root.children[2]])
		self.assertEqual(list(cache.group_by('root.tree_a').values()), [tree_a, tree_a.children[0]])

	def test_add(self) -> None:
		cache = EntryCache()
		cache.add('root', Tree('root', []))
		self.assertEqual(cache.exists('root'), True)
