from typing import cast

from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
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
		serializer.on('function', cls.on_function)
		serializer.on('if', cls.on_if)
		serializer.on('for', cls.on_for)
		serializer.on('while', cls.on_while)
		serializer.on('ternary', cls.on_ternary)
		serializer.on('op_comp', cls.on_op_comp)
		serializer.on('comp_or', cls.on_comp_logic)
		serializer.on('comp_and', cls.on_comp_logic)
		return serializer.normalize(entry)

	@classmethod
	def on_function(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(function)"""
		normalized = serializer.normalize_tree(as_a(ASTTree, entry), seq)
		block_end = normalized[-1].child_ids[-1]
		for i, normal in enumerate(normalized):
			if normal.name == 'return':
				normalized[i] = ASTNormal(normal.index, 'jump', block_end)

		return normalized

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
		normalized: list[ASTNormal] = []
		for then in thens:
			block = then[-1]
			then[-1] = ASTNormal(block.index, 'jump', if_end)
			normalized.extend(then)

		return normalized

	@classmethod
	def on_for(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(for)"""
		tree = as_a(ASTTree, entry)
		iter = serializer.normalize(tree.children[1], seq + 1)
		name = serializer.normalize(tree.children[0], iter[-1].index + 2)
		block = serializer.normalize(tree.children[2], name[-1].index + 4)
		for_begin = name[-1].index
		for_end = block[-1].index + 1
		iter_name = ASTNormal(seq, 'name', f'#{seq}')
		iter_move = ASTNormal(iter[-1].index + 1, 'move', [seq, iter[-1].index])
		iter_next = [
			ASTNormal(for_begin + 1, 'name', iter_name.string),
			ASTNormal(for_begin + 2, 'var', [for_begin + 1]),
			ASTNormal(for_begin + 3, 'next', for_end),
		]
		block[-1] = ASTNormal(block[-1].index, 'jump', for_begin)
		normalized = [iter_name, *iter, iter_move, *name, *iter_next, *block]
		for i, normal in enumerate(normalized):
			if normal.name == 'break':
				normalized[i] = ASTNormal(normal.index, 'jump', for_end)

		return normalized

	@classmethod
	def on_while(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(while)"""
		tree = as_a(ASTTree, entry)
		when = serializer.normalize(tree.children[0], seq)
		block = serializer.normalize(tree.children[1], when[-1].index + 2)
		while_end = block[-1].index + 1
		a_while = ASTNormal(when[-1].index + 1, entry.name, while_end)
		block[-1] = ASTNormal(block[-1].index, 'jump', seq)
		normalized = [*when, a_while, *block]
		for i, normal in enumerate(normalized):
			if normal.name == 'break':
				normalized[i] = ASTNormal(normal.index, 'jump', while_end)

		return normalized

	@classmethod
	def on_op_comp(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(op_comp)"""
		tree = as_a(ASTTree, entry)
		op_comp_string = ' '.join([as_a(ASTToken, child).value.string for child in tree.children])
		op_comp_s = ASTNormal(seq, 'op_comp_s', op_comp_string)
		op_comp = ASTNormal(seq + 1, tree.name, [seq])
		normalized = [op_comp_s, op_comp]
		return normalized

	@classmethod
	def on_ternary(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(ternary)"""
		tree = as_a(ASTTree, entry)
		when = serializer.normalize(tree.children[1], seq)
		left = serializer.normalize(tree.children[0], when[-1].index + 2)
		right = serializer.normalize(tree.children[2], left[-1].index + 2)
		ternary = ASTNormal(when[-1].index + 1, entry.name, right[0].index)
		jump = ASTNormal(left[-1].index + 1, 'jump', right[-1].index + 1)
		normalized = [*when, ternary, *left, jump, *right]
		return normalized

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
		normalized: list[ASTNormal] = []
		for i, op in enumerate(ops):
			if i == 0:
				normalized.extend(op)
				continue

			comp = op[-1]
			op[-1] = ASTNormal(comp.index, comp.name, ops_end)
			normalized.extend(op)

		return normalized
