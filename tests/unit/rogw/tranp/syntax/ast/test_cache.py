from typing import TypeAlias, cast
from unittest import TestCase

from rogw.tranp.syntax.ast.cache import EntryCache

DictTreeEntry: TypeAlias = tuple[str, list] | tuple[str, str]


class TestEntryCache(TestCase):
	def test_exists(self) -> None:
		cache = EntryCache[DictTreeEntry]()
		cache.add('root', ('root', []))
		self.assertEqual(True, cache.exists('root'))

	def test_by(self) -> None:
		cache = EntryCache[DictTreeEntry]()
		root = ('root', [])
		cache.add('root', root)
		self.assertEqual(root, cache.by('root'))

	def test_group_by(self) -> None:
		cache = EntryCache[DictTreeEntry]()
		root = ('root', [
			('term_a', ''),
			('tree_a', [
				('term_b', ''),
			]),
			('term_c', ''),
		])
		tree_a = cast(tuple[str, list], root[1][1])
		cache.add('root', root)
		cache.add('root.term_a', root[1][0])
		cache.add('root.tree_a', root[1][1])
		cache.add('root.tree_a.term_b', tree_a[1][0])
		cache.add('root.term_c', root[1][2])

		under_root = list(cache.group_by('root').values())
		self.assertEqual([root, root[1][0], tree_a, tree_a[1][0], root[1][2]], under_root)

		under_tree_a = list(cache.group_by('root.tree_a').values())
		self.assertEqual([tree_a, tree_a[1][0]], under_tree_a)

	def test_add(self) -> None:
		cache = EntryCache[DictTreeEntry]()
		cache.add('root', ('root', []))
		self.assertEqual(True, cache.exists('root'))
