from unittest import TestCase

from py2cpp.lang.sequence import deep_copy, update, unwrap
from tests.test.helper import data_provider


class TestSequence(TestCase):
	@data_provider([
		([1, 2], {'0': 1, '1': 2}),
		([[1], 2], {'0.0': 1, '1': 2}),
		([[1], [2]], {'0.0': 1, '1.0': 2}),
		([[1, 2], [3]], {'0.0': 1, '0.1': 2, '1.0': 3}),
		([[1, [2]], [3], 4], {'0.0': 1, '0.1.0': 2, '1.0': 3, '2': 4}),
	])
	def test_unwrap(self, entries: list, expected: dict[str, int]) -> None:
		self.assertEqual(unwrap(entries), expected)

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
		self.assertNotEqual(entries, new_entries)
		self.assertEqual(unwrap(new_entries)[path], value)

	@data_provider([
		([1, 2], '0', 3, [3, 2]),
		([[1], 2], '0.0', 4, [[4], 2]),
		([[1], 2], '1', 5, [[1], 5]),
		([[1, 2], 3], '1', 6, [[1, 2], 6]),
	])
	def test_update(self, entries: list[int], path: str, value: int, expected: list) -> None:
		update(entries, path, value)
		self.assertEqual(entries, expected)
