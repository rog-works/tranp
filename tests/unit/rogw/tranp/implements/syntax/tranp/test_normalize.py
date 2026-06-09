from unittest import TestCase

from rogw.tranp.test.helper import data_provider


class TestNormalize(TestCase):
	@data_provider([
		(
			'a if cond() else b',
			('entry', [
				('ternary', [
					('var', [
						('name', 'a'),
					]),
					('invoke', [
						('var', [
							('name', 'cond'),
						]),
						('empty', ''),
					]),
					('var', [
						('name', 'b'),
					]),
				]),
			]),
			[
				(0, 'name', 'cond'),
				(1, 'var'),
				(2, 'empty', ''),
				(3, 'invoke', [1, 2]),
				(4, 'ternary', 8),
				(5, 'name', 'a'),
				(6, 'var'),
				(7, 'jump', 10),
				(8, 'name', 'b'),
				(9, 'var'),
				(10, 'entry'),
			],
		),
	])
	def test_normalize(self, code: str, ast: tuple[str, str | list], expected: list[tuple]) -> None:
		actual = self.normalize(ast)
		self.assertEqual(expected, actual)

	def normalize(self, entry: tuple[str, str | list]) -> list[tuple]:
		return self._normalize(entry, 0)[1]

	def _normalize(self, entry: tuple[str, str | list], seq: int) -> tuple[int, list[tuple]]:
		if isinstance(entry[1], str):
			return seq, [(seq, entry[0], entry[1])]

		entries: list[tuple[int, list]] = []
		child_ids: list[int] = []
		offset = 0
		for child in entry[1]:
			child_id, normalized = self._normalize(child, seq + offset)
			child_ids.append(child_id)
			entries.extend(normalized)
			offset += len(normalized)

		tree_id = seq + offset
		entries.append((tree_id, entry[0], child_ids))
		return tree_id, entries
