from typing import TypeAlias
from unittest import TestCase

from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.lang.annotation import implements

DictTreeEntry: TypeAlias = tuple[str, list] | tuple[str, str] | None


class EntryImpl(Entry):
	def __init__(self, entry: DictTreeEntry) -> None:
		self.__entry = entry

	@property
	@implements
	def source(self) -> DictTreeEntry:
		return self.__entry

	@property
	@implements
	def name(self) -> str:
		if self.__entry is None:
			return self.empty_name
		else:
			return self.__entry[0]

	@property
	@implements
	def has_child(self) -> bool:
		return type(self.__entry[1]) is list if self.__entry is not None else False

	@property
	@implements
	def children(self) -> list[DictTreeEntry]:
		return self.__entry[1] if self.__entry is not None and type(self.__entry[1]) is list else []

	@property
	@implements
	def is_terminal(self) -> bool:
		return type(self.__entry[1]) is str if self.__entry is not None else False

	@property
	@implements
	def value(self) -> str:
		return self.__entry[1] if self.__entry is not None and type(self.__entry[1]) is str else ''

	@property
	@implements
	def is_empty(self) -> bool:
		return self.__entry is None


class TestEntry(TestCase):
	def test_source(self) -> None:
		self.assertEqual(('tree_a', []), EntryImpl(('tree_a', [])).source)

	def test_name(self) -> None:
		self.assertEqual('tree_a', EntryImpl(('tree_a', [])).name)

	def test_has_child(self) -> None:
		self.assertEqual(True, EntryImpl(('tree_a', [])).has_child)

	def test_children(self) -> None:
		self.assertEqual([('term_a', 'a')], EntryImpl(('tree_a', [('term_a', 'a')])).children)

	def test_is_terminal(self) -> None:
		self.assertEqual(True, EntryImpl(('term_a', 'a')).is_terminal)

	def test_value(self) -> None:
		self.assertEqual('a', EntryImpl(('term_a', 'a')).value)

	def test_is_empty(self) -> None:
		self.assertEqual(False, EntryImpl(('term_a', 'a')).is_empty)

	def test_source_map(self) -> None:
		self.assertEqual({'begin': (0, 0), 'end': (0, 0)}, EntryImpl(('term_a', 'a')).source_map)
