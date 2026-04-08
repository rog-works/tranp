from unittest import TestCase

from rogw.tranp.compatible.cpp.classes import digit, double, uint64
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
		(uint64(3), '&', 1, 1),
		(uint64(3), '|', 1, 3),
		(uint64(3), '^', 1, 2),
		(uint64(1), '<<', 2, 4),
		(uint64(4), '>>', 1, 2),
	])
	def test_operation(self, left: digit, operator: str, right: int, expected: bool | int) -> None:
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
		elif operator == '&':
			actual = left & right
		elif operator == '|':
			actual = left | right
		elif operator == '^':
			actual = left ^ right
		elif operator == '<<':
			actual = left << right
		elif operator == '>>':
			actual = left >> right

		self.assertEqual(actual, expected)


class TestDouble(TestCase):
	@data_provider([
		(double(1.0), '==', 1.0, True),
		(double(1.0), '!=', 1.0, False),
		(double(1.0), '<', 2.0, True),
		(double(1.0), '>', 2.0, False),
		(double(2.0), '<=', 2.0, True),
		(double(2.0), '>=', 2.0, True),
		(double(1.0), '+', 1.0, 2.0),
		(double(1.0), '-', 1.0, 0.0),
		(double(3.0), '*', 2.0, 6.0),
		(double(3.0), '/', 2.0, 1.5),
		(double(5.0), '%', 3.0, 2.0),
	])
	def test_operation(self, left: double, operator: str, right: float, expected: bool | float) -> None:
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
