from unittest import TestCase

from data.syntax.py_rules import py_rules
from data.syntax.py_serializer import PythonASTSerializer
from rogw.tranp.implements.syntax.tranp.serializer import ASTNormal
from rogw.tranp.implements.syntax.tranp.syntax import SyntaxParser
from rogw.tranp.test.helper import data_provider


class TestNormalize(TestCase):
	@data_provider([
		(
			'\n'.join([
				'while a:',
				'  b',
			]),
			[
				(0, 'name', 'a'),
				(1, 'var', [0]),
				(2, 'name', 'b'),
				(3, 'var', [2]),
				(4, 'block', [3]),
				(5, 'while', [1, 4]),
				(6, 'entry', [5]),
			],
		),
		(
			'(a and b and c) and d',
			[
				(0, 'name', 'a'),
				(1, 'var', [0]),
				(2, 'op_and', 'and'),
				(3, 'name', 'b'),
				(4, 'var', [3]),
				(5, 'comp_and', 10),
				(6, 'op_and', 'and'),
				(7, 'name', 'c'),
				(8, 'var', [7]),
				(9, 'comp_and', 10),
				(10, 'op_and', 'and'),
				(11, 'name', 'd'),
				(12, 'var', [11]),
				(13, 'comp_and', 14),
				(14, 'entry', [13]),
			],
		),
		(
			'a if cond() else b',
			[
				(0, 'name', 'cond'),
				(1, 'var', [0]),
				(2, '__empty__', ''),
				(3, 'invoke', [1, 2]),
				(4, 'ternary', 8),
				(5, 'name', 'a'),
				(6, 'var', [5]),
				(7, 'jump', 10),
				(8, 'name', 'b'),
				(9, 'var', [8]),
				(10, 'entry', [9]),
			],
		),
		(
			'\n'.join([
				'if a:',
				'  b == c',
				'else:',
				'  d',
			]),
			[
				# --- if a:
				(0, 'name', 'a'),
				(1, 'var', [0]),
				(2, 'then', 11),
				(3, 'name', 'b'),
				(4, 'var', [3]),
				(5, 'op_comp_s', '=='),
				(6, 'op_comp', [5]),
				(7, 'name', 'c'),
				(8, 'var', [7]),
				(9, 'comp', [4, 6, 8]),
				(10, 'jump', 15),
				# --- else:
				(11, 'else', 15),
				(12, 'name', 'd'),
				(13, 'var', [12]),
				(14, 'jump', 15),
				# ---
				(15, 'entry', [14]),
			],
		),
		(
			'\n'.join([
				'if a:',
				'  b',
				'elif c:',
				'  d',
			]),
			[
				# --- if a:
				(0, 'name', 'a'),
				(1, 'var', [0]),
				(2, 'then', 6),
				(3, 'name', 'b'),
				(4, 'var', [3]),
				(5, 'jump', 12),
				# --- elif b:
				(6, 'name', 'c'),
				(7, 'var', [6]),
				(8, 'elif', 12),
				(9, 'name', 'd'),
				(10, 'var', [9]),
				(11, 'jump', 12),
				# ---
				(12, 'entry', [11]),
			],
		),
	])
	def test_normalize(self, code: str, expected: list[ASTNormal]) -> None:
		parser = SyntaxParser(py_rules())
		tree = parser.parse(code, 'entry')
		actual = PythonASTSerializer.normalize(tree)
		try:
			self.assertEqual(expected, actual)
		except AssertionError:
			for entry in actual:
				print(*entry, sep=', ')

			raise
