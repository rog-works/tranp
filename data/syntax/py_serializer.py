from typing import cast

from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTTree
from rogw.tranp.implements.syntax.tranp.serializer import ASTNormal, ASTSerializer
from rogw.tranp.lang.convertion import as_a


class PythonASTSerializer:
	"""ASTシリアライザー(Python)"""

	@classmethod
	def normalize(cls, entry: ASTEntry) -> list[ASTNormal]:
		"""ASTを正規化

		Args:
			entry: ASTエントリー
		Returns:
			正規化したAST
		"""
		serializer = ASTSerializer()
		serializer.on('if', cls.on_if)
		serializer.on('ternary', cls.on_ternary)
		serializer.on('comp_or', cls.on_comp_logic)
		serializer.on('comp_and', cls.on_comp_logic)
		return serializer.normalize(entry)

	@classmethod
	def on_comp_logic(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(comp_or/comp_and)"""
		tree = as_a(ASTTree, entry)
		ops_count = int((len(tree.children) - 1) / 2)
		ops = [serializer.normalize(tree.children[0], seq)]
		ops_seq = ops[0][-1].index + 1
		for i in range(ops_count):
			index = i * 2 + 1
			op = serializer.normalize(tree.children[index + 0], ops_seq)
			right = serializer.normalize(tree.children[index + 1], op[-1].index + 1)
			comp = ASTNormal(right[-1].index + 1, entry.name, -1)
			ops.append([*op, *right, comp])
			ops_seq = comp.index + 1

		ops_end = ops_seq
		entries: list[ASTNormal] = []
		for i, op in enumerate(ops):
			if i == 0:
				entries.extend(op)
				continue

			comp = op[-1]
			op[-1] = ASTNormal(comp.index, comp.name, ops_end)
			entries.extend(op)

		return entries

	@classmethod
	def on_if(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(if)"""
		tree = as_a(ASTTree, entry)
		thens: list[list[ASTNormal]] = []
		then_seq = seq
		for child in cast(list[ASTTree], tree.children):
			if child.name == '__empty__':
				...
			elif child.name != 'else':
				cond = serializer.normalize(child.children[0], then_seq)
				block = serializer.normalize(child.children[1], cond[-1].index + 2)
				then = ASTNormal(cond[-1].index + 1, child.name, block[-1].index + 1)
				thens.append([*cond, then, *block])
				then_seq = then.context
			else:
				block = serializer.normalize(child.children[0], then_seq + 1)
				a_else = ASTNormal(then_seq, child.name, block[-1].index + 1)
				thens.append([a_else, *block])
				then_seq = a_else.context

		if_end = then_seq
		entries: list[ASTNormal] = []
		for then in thens:
			block = then[-1]
			then[-1] = ASTNormal(block.index, 'jump', if_end)
			entries.extend(then)

		return entries

	@classmethod
	def on_ternary(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(ternary)"""
		tree = as_a(ASTTree, entry)
		cond = serializer.normalize(tree.children[1], seq)
		left = serializer.normalize(tree.children[0], cond[-1].index + 2)
		right = serializer.normalize(tree.children[2], left[-1].index + 2)
		ternary = ASTNormal(cond[-1].index + 1, entry.name, right[0].index)
		jump = ASTNormal(left[-1].index + 1, 'jump', right[-1].index + 1)
		entries = [*cond, ternary, *left, jump, *right]
		return entries
