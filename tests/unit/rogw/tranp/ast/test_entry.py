from typing import TypeAlias
from unittest import TestCase

from rogw.tranp.ast.entry import Entry
from rogw.tranp.lang.implementation import implements

T_Entry: TypeAlias = tuple[str, list] | tuple[str, str] | None


class EntryImpl(Entry):
	def __init__(self, entry: T_Entry) -> None:
		self.__entry = entry

	@property
	@implements
	def source(self) -> T_Entry:
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
	def children(self) -> list[T_Entry]:
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
		self.assertEqual(EntryImpl(('tree_a', [])).source, ('tree_a', []))

	def test_name(self) -> None:
		self.assertEqual(EntryImpl(('tree_a', [])).name, 'tree_a')

	def test_has_child(self) -> None:
		self.assertEqual(EntryImpl(('tree_a', [])).has_child, True)

	def test_children(self) -> None:
		self.assertEqual(EntryImpl(('tree_a', [('term_a', 'a')])).children, [('term_a', 'a')])

	def test_is_terminal(self) -> None:
		self.assertEqual(EntryImpl(('term_a', 'a')).is_terminal, True)

	def test_value(self) -> None:
		self.assertEqual(EntryImpl(('term_a', 'a')).value, 'a')

	def test_is_empty(self) -> None:
		self.assertEqual(EntryImpl(('term_a', 'a')).is_empty, False)
