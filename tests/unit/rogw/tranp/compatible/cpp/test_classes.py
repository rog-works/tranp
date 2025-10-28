from unittest import TestCase

from rogw.tranp.compatible.cpp.classes import digit, uint64
from rogw.tranp.test.helper import data_provider


class TestDigit(TestCase):
	@data_provider([
		(uint64(1), '==', 1, True),
		(uint64(1), '!=', 1, False),
		(uint64(1), '<', 2, True),
		(uint64(1), '>', 2, False),
		(uint64(2), '<=', 2, True),
		(uint64(2), '>=', 2, True),
		(uint64(1), '+', 1, 2),
		(uint64(1), '-', 1, 0),
		(uint64(3), '*', 2, 6),
		(uint64(3), '/', 2, 1),
		(uint64(5), '%', 3, 2),
	])
	def test_operators(self, left: digit, operator: str, right: int | digit, expected: bool | int | digit) -> None:
		actual = 0
		if operator == '==':
			actual = left == right
		elif operator == '!=':
			actual = left != right
		elif operator == '<':
			actual = left < right
		elif operator == '>':
			actual = left > right
		elif operator == '<=':
			actual = left <= right
		elif operator == '>=':
			actual = left >= right
		elif operator == '+':
			actual = left + right
		elif operator == '-':
			actual = left - right
		elif operator == '*':
			actual = left * right
		elif operator == '/':
			actual = left / right
		elif operator == '%':
			actual = left % right

		self.assertEqual(actual, expected)
