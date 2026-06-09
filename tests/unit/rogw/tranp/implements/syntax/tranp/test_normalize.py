from collections.abc import Callable
from typing import Any, TypeAlias, cast
from unittest import TestCase

from rogw.tranp.lang.middleware import Middleware
from rogw.tranp.test.helper import data_provider

Token: TypeAlias = tuple[str, str]
Node: TypeAlias = tuple[str, 'list[Token | Node]']
AST: TypeAlias = Token | Node

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
				(1, 'var', [0]),
				(2, 'empty', ''),
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
	])
	def test_normalize(self, code: str, ast: AST, expected: list[tuple]) -> None:
		serializer = ASTSerializer()
		serializer.on('ternary', self.on_ternary)
		actual = serializer.normalize(ast)
		self.assertEqual(expected, actual)

	def on_ternary(self, serializer: 'ASTSerializer', entry: Node, seq: int) -> list[tuple]:
		cond = serializer.normalize(entry[1][1], seq)
		ternary = (cond[-1][0] + 1, entry[0], -1)
		left = serializer.normalize(entry[1][0], ternary[0] + 1)
		jump = (left[-1][0] + 1, 'jump', -1)
		right = serializer.normalize(entry[1][2], jump[0] + 1)
		ternary = (ternary[0], ternary[1], right[0][0])
		jump = (jump[0], jump[1], right[-1][0] + 1)
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
