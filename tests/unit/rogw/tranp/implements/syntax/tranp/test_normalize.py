from typing import Any, TypeAlias, cast
from unittest import TestCase

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
		actual = ASTSerializer.normalize(ast)
		self.assertEqual(expected, actual)


class ASTSerializer:
	@classmethod
	def normalize(cls, entry: AST) -> list[tuple]:
		return cls._normalize(entry, 0)

	@classmethod
	def _normalize(cls, entry: AST, seq: int) -> list[tuple]:
		if isinstance(entry[1], str):
			return cls._normalize_token(cast(Token, entry), seq)

		spec = f'on_{entry[0]}'
		if hasattr(cls, spec):
			return getattr(cls, spec)(cast(Node, entry), seq)
		else:
			return cls._normalize_node(cast(Node, entry), seq)

	@classmethod
	def _normalize_token(cls, entry: Token, seq: int) -> list[tuple]:
		return [(seq, entry[0], entry[1])]

	@classmethod
	def _normalize_node(cls, entry: Node, seq: int) -> list[tuple]:
		entries: list[tuple[int, str, Any]] = []
		child_ids: list[int] = []
		offset = 0
		for child in entry[1]:
			normalized = cls._normalize(child, seq + offset)
			child_ids.append(normalized[-1][0])
			entries.extend(normalized)
			offset += len(normalized)

		tree_id = seq + offset
		entries.append((tree_id, entry[0], child_ids))
		return entries
	
	@classmethod
	def on_ternary(cls, entry: Node, seq: int) -> list[tuple]:
		cond = cls._normalize(entry[1][1], seq)
		ternary = (cond[-1][0] + 1, entry[0], -1)
		left = cls._normalize(entry[1][0], ternary[0] + 1)
		jump = (left[-1][0] + 1, 'jump', -1)
		right = cls._normalize(entry[1][2], jump[0] + 1)
		ternary = (ternary[0], ternary[1], right[0][0])
		jump = (jump[0], jump[1], right[-1][0] + 1)
		entries = [*cond, ternary, *left, jump, *right]
		return entries
