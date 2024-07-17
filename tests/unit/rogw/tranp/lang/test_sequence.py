from typing import Any, NamedTuple
from unittest import TestCase

from rogw.tranp.lang.sequence import index_of, last_index_of, deep_copy, update, expand
from rogw.tranp.test.helper import data_provider


class Each(NamedTuple):
	value: int
	attrs: list['Each'] = []

	def __repr__(self) -> str:
		return f'<Each: {self.value}, [{", ".join([str(attr) for attr in self.attrs])}]>'

	def __eq__(self, other: Any) -> bool:
		return type(other) is Each and other.__repr__() == self.__repr__()


class TestSequence(TestCase):
	@data_provider([
		([1, 2], 1, 0),
		([1, 2], 2, 1),
		([1, 2], 3, -1),
	])
	def test_index_of(self, arr: list[int], search: int, expected: int) -> None:
		self.assertEqual(index_of(arr, search), expected)

	@data_provider([
		([1, 2, 2, 1, 3], 1, 3),
		([1, 2, 2, 1, 3], 2, 2),
		([1, 2, 2, 1, 3], 3, 4),
		([1, 2, 2, 1, 3], 4, -1),
	])
	def test_last_index_of(self, arr: list[int], search: int, expected: int) -> None:
		self.assertEqual(last_index_of(arr, search), expected)

	@data_provider([
		([1, 2], None, {'0': 1, '1': 2}),
		([[1], 2], None, {'0.0': 1, '1': 2}),
		([[1], [2]], None, {'0.0': 1, '1.0': 2}),
		([[1, 2], [3]], None, {'0.0': 1, '0.1': 2, '1.0': 3}),
		([[1, [2]], [3], 4], None, {'0.0': 1, '0.1.0': 2, '1.0': 3, '2': 4}),
		({'a': 1}, None, {'a': 1}),
		({'a': [1]}, None, {'a.0': 1}),
		({'a': [1, {'b': 2}]}, None, {'a.0': 1, 'a.1.b': 2}),
		([Each(1), Each(2)], 'attrs', {'0': Each(1), '1': Each(2)}),
		([Each(1, [Each(2)]), Each(3)], 'attrs', {'0': Each(1, [Each(2)]), '0.0': Each(2), '1': Each(3)}),
	])
	def test_expand(self, entries: list | dict, iter_key: str | None, expected: dict[str, int]) -> None:
		self.assertEqual(expand(entries, iter_key=iter_key), expected)

	@data_provider([
		([1, 2], '0', 3, None, [3, 2]),
		([[1], 2], '0.0', 4, None, [[4], 2]),
		([[1], 2], '1', 5, None, [[1], 5]),
		([[1, 2], 3], '1', 6, None, [[1, 2], 6]),
		({'a': 1}, 'a', 2, None, {'a': 2}),
		({'a': [1]}, 'a.0', 2, None, {'a': [2]}),
		({'a': [1, {'b': 2}]}, 'a.1.b', 3, None, {'a': [1, {'b': 3}]}),
		([Each(1), Each(2)], '1', Each(3), 'attrs', [Each(1), Each(3)]),
		([Each(1, [Each(2)]), Each(3)], '0.0', Each(4), 'attrs', [Each(1, [Each(4)]), Each(3)]),
	])
	def test_update(self, entries: list | dict, path: str, value: int, iter_key: str | None, expected: list | dict) -> None:
		update(entries, path, value, iter_key=iter_key)
		self.assertEqual(entries, expected)

	@data_provider([
		([1, 2], ('0', 3)),
		([[1, 2], 3], ('0.1', 4)),
		([1, [2, 3]], ('1.0', 5)),
	])
	def test_deep_copy(self, entries: list, test_values: tuple[str, int]) -> None:
		new_entries = deep_copy(entries)
		self.assertEqual(entries, new_entries)

		path, value = test_values
		update(new_entries, path, value)
		self.assertNotEqual(new_entries, entries)
		self.assertEqual(expand(new_entries)[path], value)
