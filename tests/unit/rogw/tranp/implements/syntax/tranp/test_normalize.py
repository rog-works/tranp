from typing import cast
from unittest import TestCase

from data.syntax.py_rules import py_rules
from rogw.tranp.implements.syntax.tranp.ast import ASTTree
from rogw.tranp.implements.syntax.tranp.serializer import ASTSerializer, IdContext, IdIndex
from rogw.tranp.implements.syntax.tranp.syntax import SyntaxParser
from rogw.tranp.test.helper import data_provider


class TestNormalize(TestCase):
	@data_provider([
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
	def test_normalize(self, code: str, expected: list[tuple]) -> None:
		serializer = ASTSerializer()
		serializer.on('if', self.on_if)
		serializer.on('ternary', self.on_ternary)

		parser = SyntaxParser(py_rules())
		tree = parser.parse(code, 'entry')
		actual = serializer.normalize(tree)
		try:
			self.assertEqual(expected, actual)
		except AssertionError:
			for entry in actual:
				print(entry)

			raise

	def on_if(self, serializer: ASTSerializer, entry: ASTTree, seq: int) -> list[tuple]:
		thens: list[list[tuple]] = []
		then_seq = seq
		for child in cast(list[ASTTree], entry.children):
			if child.name == '__empty__':
				...
			elif child.name != 'else':
				cond = serializer.normalize(child.children[0], then_seq)
				block = serializer.normalize(child.children[1], cond[-1][IdIndex] + 2)
				then = (cond[-1][IdIndex] + 1, child.name, block[-1][IdIndex] + 1)
				thens.append([*cond, then, *block])
				then_seq = then[IdContext]
			else:
				block = serializer.normalize(child.children[0], then_seq + 1)
				a_else = (then_seq, child.name, block[-1][IdIndex] + 1)
				thens.append([a_else, *block])
				then_seq = a_else[IdContext]

		if_end = then_seq
		entries: list[tuple] = []
		for then in thens:
			block = then[-1]
			then[-1] = (block[IdIndex], 'jump', if_end)
			entries.extend(then)

		return entries

	def on_ternary(self, serializer: ASTSerializer, entry: ASTTree, seq: int) -> list[tuple]:
		cond = serializer.normalize(entry.children[1], seq)
		left = serializer.normalize(entry.children[0], cond[-1][IdIndex] + 2)
		right = serializer.normalize(entry.children[2], left[-1][IdIndex] + 2)
		ternary = (cond[-1][IdIndex] + 1, entry.name, right[0][IdIndex])
		jump = (left[-1][IdIndex] + 1, 'jump', right[-1][IdIndex] + 1)
		entries = [*cond, ternary, *left, jump, *right]
		return entries
