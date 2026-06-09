from collections.abc import Callable
from typing import Any, Literal, TypeAlias, cast
from unittest import TestCase

from rogw.tranp.lang.middleware import Middleware
from rogw.tranp.test.helper import data_provider

Token: TypeAlias = tuple[str, str]
Node: TypeAlias = tuple[str, 'list[Token | Node]']
AST: TypeAlias = Token | Node

Name: Literal[0] = 0
Children: Literal[1] = 1

Id: Literal[0] = 0
Comm: Literal[1] = 1
Ctx: Literal[2] = 2

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
						('__empty__', ''),
					]),
					('var', [
						('name', 'b'),
					]),
				]),
			]),
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
			('entry', [
				('if', [
					('then', [
						('var', [
							('name', 'a'),
						]),
						('block', [
							('comp', [
								('var', [
									('name', 'b'),
								]),
								('op_comp', [
									('op_comp_s', '=='),
								]),
								('var', [
									('name', 'c'),
								]),
							]),
						]),
					]),
					('else', [
						('block', [
							('var', [
								('name', 'd'),
							]),
						]),
					]),
				]),
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
	def test_normalize(self, code: str, ast: AST, expected: list[tuple]) -> None:
		serializer = ASTSerializer()
		serializer.on('if', self.on_if)
		serializer.on('ternary', self.on_ternary)
		actual = serializer.normalize(ast)
		self.assertEqual(expected, actual)

	def on_if(self, serializer: 'ASTSerializer', entry: Node, seq: int) -> list[tuple]:
		thens: list[list[tuple]] = []
		then_seq = seq
		for child in cast(list[Node], entry[Children]):
			if child[Name] != 'else':
				cond = serializer.normalize(child[Children][0], then_seq)
				block = serializer.normalize(child[Children][1], cond[-1][Id] + 2)
				then = (cond[-1][Id] + 1, child[Name], block[-1][Id] + 1)
				thens.append([*cond, then, *block])
				then_seq = then[Ctx]
			else:
				block = serializer.normalize(child[Children][0], then_seq + 1)
				a_else = (then_seq, child[Name], block[-1][Id] + 1)
				thens.append([a_else, *block])
				then_seq = a_else[Ctx]

		if_end = then_seq
		entries: list[tuple] = []
		for then in thens:
			block = then[-1]
			then[-1] = (block[Id], 'jump', if_end)
			entries.extend(then)

		return entries

	def on_ternary(self, serializer: 'ASTSerializer', entry: Node, seq: int) -> list[tuple]:
		cond = serializer.normalize(entry[Children][1], seq)
		left = serializer.normalize(entry[Children][0], cond[-1][Id] + 2)
		right = serializer.normalize(entry[Children][2], left[-1][Id] + 2)
		ternary = (cond[-1][Id] + 1, entry[Name], right[0][Id])
		jump = (left[-1][Id] + 1, 'jump', right[-1][Id] + 1)
		entries = [*cond, ternary, *left, jump, *right]
		return entries


class ASTSerializer:
	def __init__(self) -> None:
		self._middleware = Middleware[list[tuple]]()

	def on(self, action: str, callback: Callable[['ASTSerializer', Node, int], list[tuple]]) -> None:
		self._middleware.on(action, callback)

	def normalize(self, entry: AST, seq: int = 0) -> list[tuple]:
		if self._middleware.usable(entry[0]):
			return self._middleware.emit(entry[0], serializer=self, entry=entry, seq=seq)
		elif isinstance(entry[1], str):
			return self.normalize_token(cast(Token, entry), seq)
		else:
			return self.normalize_node(cast(Node, entry), seq)

	def normalize_token(self, entry: Token, seq: int) -> list[tuple]:
		return [(seq, entry[0], entry[1])]

	def normalize_node(self, entry: Node, seq: int) -> list[tuple]:
		entries: list[tuple[int, str, Any]] = []
		child_ids: list[int] = []
		offset = 0
		for child in entry[1]:
			normalized = self.normalize(child, seq + offset)
			child_ids.append(normalized[-1][0])
			entries.extend(normalized)
			offset += len(normalized)

		tree_id = seq + offset
		entries.append((tree_id, entry[0], child_ids))
		return entries
