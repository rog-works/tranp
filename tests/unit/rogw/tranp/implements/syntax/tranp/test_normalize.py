from collections.abc import Callable
from typing import Any, Literal, cast
from unittest import TestCase

from data.syntax.py_rules import py_rules
from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
from rogw.tranp.implements.syntax.tranp.syntax import SyntaxParser
from rogw.tranp.lang.middleware import Middleware
from rogw.tranp.test.helper import data_provider

Id: Literal[0] = 0
Comm: Literal[1] = 1
Ctx: Literal[2] = 2

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

	def on_if(self, serializer: 'ASTSerializer', entry: ASTTree, seq: int) -> list[tuple]:
		thens: list[list[tuple]] = []
		then_seq = seq
		for child in cast(list[ASTTree], entry.children):
			if child.name != 'else':
				cond = serializer.normalize(child.children[0], then_seq)
				block = serializer.normalize(child.children[1], cond[-1][Id] + 2)
				then = (cond[-1][Id] + 1, child.name, block[-1][Id] + 1)
				thens.append([*cond, then, *block])
				then_seq = then[Ctx]
			else:
				block = serializer.normalize(child.children[0], then_seq + 1)
				a_else = (then_seq, child.name, block[-1][Id] + 1)
				thens.append([a_else, *block])
				then_seq = a_else[Ctx]

		if_end = then_seq
		entries: list[tuple] = []
		for then in thens:
			block = then[-1]
			then[-1] = (block[Id], 'jump', if_end)
			entries.extend(then)

		return entries

	def on_ternary(self, serializer: 'ASTSerializer', entry: ASTTree, seq: int) -> list[tuple]:
		cond = serializer.normalize(entry.children[1], seq)
		left = serializer.normalize(entry.children[0], cond[-1][Id] + 2)
		right = serializer.normalize(entry.children[2], left[-1][Id] + 2)
		ternary = (cond[-1][Id] + 1, entry.name, right[0][Id])
		jump = (left[-1][Id] + 1, 'jump', right[-1][Id] + 1)
		entries = [*cond, ternary, *left, jump, *right]
		return entries


class ASTSerializer:
	def __init__(self) -> None:
		self._middleware = Middleware[list[tuple]]()

	def on(self, action: str, callback: Callable[['ASTSerializer', ASTTree, int], list[tuple]]) -> None:
		self._middleware.on(action, callback)

	def normalize(self, entry: ASTEntry, seq: int = 0) -> list[tuple]:
		if self._middleware.usable(entry.name):
			return self._middleware.emit(entry.name, serializer=self, entry=entry, seq=seq)
		elif isinstance(entry, ASTToken):
			return self.normalize_token(entry, seq)
		else:
			return self.normalize_node(entry, seq)

	def normalize_token(self, entry: ASTToken, seq: int) -> list[tuple]:
		return [(seq, entry.name, entry.value.string)]

	def normalize_node(self, entry: ASTTree, seq: int) -> list[tuple]:
		entries: list[tuple[int, str, Any]] = []
		child_ids: list[int] = []
		offset = 0
		for child in entry.children:
			normalized = self.normalize(child, seq + offset)
			child_ids.append(normalized[-1][Id])
			entries.extend(normalized)
			offset += len(normalized)

		tree_id = seq + offset
		entries.append((tree_id, entry.name, child_ids))
		return entries
