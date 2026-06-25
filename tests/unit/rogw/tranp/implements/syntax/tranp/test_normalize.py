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
				'a is not None',
				'b not in []',
			]),
			[
				(0, 'name', 'a'),
				(1, 'var', [0]),
				(2, 'op_comp', 'is not'),
				(3, 'none', 'None'),
				(4, 'comp', [1, 2, 3]),
				(5, 'name', 'b'),
				(6, 'var', [5]),
				(7, 'op_comp', 'not in'),
				(8, '__empty__', ''),
				(9, 'list', [8]),
				(10, 'comp', [6, 7, 9]),
				(11, 'entry', [4, 10]),
			],
		),
		(
			'\n'.join([
				'a.b = c',
			]),
			[
				(0, 'name', 'a'),
				(1, 'var', [0]),
				(2, 'name', 'b'),
				(3, 'name', 'c'),
				(4, 'var', [3]),
				(5, 'move', [1, 2, 4]),
				(6, 'entry', [5]),
			],
		),
		(
			'\n'.join([
				'for a in b:',
				'  for c in d:',
				'    break',
				'  break',
			]),
			[
				# for a in b:
				(0, 'name', '#0'),
				(1, 'name', 'b'),
				(2, 'var', [1]),
				(3, 'move', [0, 2]),
				# block #0
				(4, 'name', 'a'),
				(5, 'name', '#0'),
				(6, 'var', [5]),
				(7, 'next', 20),
				# for c in d:
				(8, 'name', '#8'),
				(9, 'name', 'd'),
				(10, 'var', [9]),
				(11, 'move', [8, 10]),
				# block #1
				(12, 'name', 'c'),
				(13, 'name', '#8'),
				(14, 'var', [13]),
				(15, 'next', 18),
				(16, 'jump', 18),
				(17, 'jump', 12),
				# / block #1
				(18, 'jump', 20),
				(19, 'jump', 4),
				# / block #0
				(20, 'entry', [19]),
			],
		),
		(
			'\n'.join([
				'def f() -> None:',
				'  a = 0',
				'  return a',
			]),
			[
				(0, 'name', 'f'),
				(1, '__empty__', ''),
				(2, 'none', 'None'),
				(3, 'type_none', [2]),
				# block
				(4, 'name', 'a'),
				(5, 'digit', '0'),
				(6, 'move', [4, 5]),
				(7, 'name', 'a'),
				(8, 'var', [7]),
				(9, 'jump', 10),
				(10, 'block', [6, 9]),
				# / block
				(11, 'function', [0, 1, 3, 10]),
				(12, 'entry', [11]),
			],
		),
		(
			'\n'.join([
				'while a:',
				'  while b:',
				'    break',
				'  break',
			]),
			[
				# while a:
				(0, 'name', 'a'),
				(1, 'var', [0]),
				(2, 'while', 10),
				# while b:
				(3, 'name', 'b'),
				(4, 'var', [3]),
				(5, 'while', 8),
				(6, 'jump', 8),
				(7, 'jump', 3),
				# / while b:
				(8, 'jump', 10),
				(9, 'jump', 0),
				# / while a:
				(10, 'entry', [9]),
			],
		),
		(
			'(a and b and c) and d',
			[
				# a and b
				(0, 'name', 'a'),
				(1, 'var', [0]),
				(2, 'op_and', 'and'),
				(3, 'name', 'b'),
				(4, 'var', [3]),
				(5, 'comp_and', 10),
				# $ and c
				(6, 'op_and', 'and'),
				(7, 'name', 'c'),
				(8, 'var', [7]),
				(9, 'comp_and', 10),
				# / a and c
				# $ and d
				(10, 'op_and', 'and'),
				(11, 'name', 'd'),
				(12, 'var', [11]),
				(13, 'comp_and', 14),
				# / $ and d
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
				# / ternary
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
				# if a:
				(0, 'name', 'a'),
				(1, 'var', [0]),
				(2, 'then', 10),
				(3, 'name', 'b'),
				(4, 'var', [3]),
				(5, 'op_comp', '=='),
				(6, 'name', 'c'),
				(7, 'var', [6]),
				(8, 'comp', [4, 5, 7]),
				(9, 'jump', 14),
				# else:
				(10, 'else', 14),
				(11, 'name', 'd'),
				(12, 'var', [11]),
				(13, 'jump', 14),
				# / else:
				# / if a:
				(14, 'entry', [13]),
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
				# if a:
				(0, 'name', 'a'),
				(1, 'var', [0]),
				(2, 'then', 6),
				(3, 'name', 'b'),
				(4, 'var', [3]),
				(5, 'jump', 12),
				# elif b:
				(6, 'name', 'c'),
				(7, 'var', [6]),
				(8, 'elif', 12),
				(9, 'name', 'd'),
				(10, 'var', [9]),
				(11, 'jump', 12),
				# / if b:
				# / if a:
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
