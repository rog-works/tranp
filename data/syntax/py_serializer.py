from typing import cast

from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
from rogw.tranp.implements.syntax.tranp.serializer import ASTNormal, ASTSerializer
from rogw.tranp.lang.convertion import as_a


class PythonASTSerializer:
	"""ASTシリアライザー(Python)"""

	class Rules:
		"""Grammarルール名"""
		# 分/ブロック
		Function = 'function'
		# 分/代入
		Move = 'move'
		# 分/行
		Break = 'break'
		Return = 'return'
		# 式/ブロック
		If = 'if'
		Else = 'else'
		For = 'for'
		While = 'while'
		# 式/演算
		Ternary = 'ternary'
		OpComp = 'op_comp'
		CompOr = 'comp_or'
		CompAnd = 'comp_and'
		# 式/チェーン
		Invoke = 'invoke'
		# 終端要素
		Var = 'var'
		Name = 'name'
		# 拡張コマンド
		Empty = '__empty__'
		Jump = 'jump'
		Next = 'next'

	@classmethod
	def normalize(cls, entry: ASTEntry) -> list[ASTNormal]:
		"""ASTを正規化

		Args:
			entry: ASTエントリー
		Returns:
			正規化したAST
		"""
		serializer = ASTSerializer()
		serializer.on(cls.Rules.Function, cls.on_function)
		serializer.on(cls.Rules.If, cls.on_if)
		serializer.on(cls.Rules.For, cls.on_for)
		serializer.on(cls.Rules.While, cls.on_while)
		serializer.on(cls.Rules.Ternary, cls.on_ternary)
		serializer.on(cls.Rules.OpComp, cls.on_op_comp)
		serializer.on(cls.Rules.CompOr, cls.on_comp_logic)
		serializer.on(cls.Rules.CompAnd, cls.on_comp_logic)
		serializer.on(cls.Rules.Invoke, cls.on_invoke)
		return serializer.normalize(entry)

	@classmethod
	def on_function(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(function)"""
		normalized = serializer.normalize_tree(as_a(ASTTree, entry), seq)
		block_end = normalized[-1].child_ids[-1]
		for i, normal in enumerate(normalized):
			if normal.name == cls.Rules.Return:
				normalized[i] = ASTNormal(normal.index, cls.Rules.Jump, block_end)

		return normalized

	@classmethod
	def on_if(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(if)"""
		tree = as_a(ASTTree, entry)
		thens: list[list[ASTNormal]] = []
		then_seq = seq
		for child in cast(list[ASTTree], tree.children):
			if child.name == cls.Rules.Empty:
				...
			elif child.name != cls.Rules.Else:
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
			then[-1] = ASTNormal(block.index, cls.Rules.Jump, if_end)
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
		iter_name = ASTNormal(seq, cls.Rules.Name, f'#{seq}')
		iter_move = ASTNormal(iter[-1].index + 1, cls.Rules.Move, [seq, iter[-1].index])
		iter_next = [
			ASTNormal(for_begin + 1, cls.Rules.Name, iter_name.string),
			ASTNormal(for_begin + 2, cls.Rules.Var, [for_begin + 1]),
			ASTNormal(for_begin + 3, cls.Rules.Next, for_end),
		]
		block[-1] = ASTNormal(block[-1].index, cls.Rules.Jump, for_begin)
		normalized = [iter_name, *iter, iter_move, *name, *iter_next, *block]
		for i, normal in enumerate(normalized):
			if normal.name == cls.Rules.Break:
				normalized[i] = ASTNormal(normal.index, cls.Rules.Jump, for_end)

		return normalized

	@classmethod
	def on_while(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(while)"""
		tree = as_a(ASTTree, entry)
		when = serializer.normalize(tree.children[0], seq)
		block = serializer.normalize(tree.children[1], when[-1].index + 2)
		while_end = block[-1].index + 1
		a_while = ASTNormal(when[-1].index + 1, entry.name, while_end)
		block[-1] = ASTNormal(block[-1].index, cls.Rules.Jump, seq)
		normalized = [*when, a_while, *block]
		for i, normal in enumerate(normalized):
			if normal.name == cls.Rules.Break:
				normalized[i] = ASTNormal(normal.index, cls.Rules.Jump, while_end)

		return normalized

	@classmethod
	def on_op_comp(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(op_comp)"""
		tree = as_a(ASTTree, entry)
		op_comp_string = ' '.join([as_a(ASTToken, child).value.string for child in tree.children])
		op_comp = ASTNormal(seq, tree.name, op_comp_string)
		return [op_comp]

	@classmethod
	def on_ternary(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(ternary)"""
		tree = as_a(ASTTree, entry)
		when = serializer.normalize(tree.children[1], seq)
		left = serializer.normalize(tree.children[0], when[-1].index + 2)
		right = serializer.normalize(tree.children[2], left[-1].index + 2)
		ternary = ASTNormal(when[-1].index + 1, entry.name, right[0].index)
		jump = ASTNormal(left[-1].index + 1, cls.Rules.Jump, right[-1].index + 1)
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

	@classmethod
	def on_invoke(cls, serializer: ASTSerializer, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(invoke)"""
		tree = as_a(ASTTree, entry)

		normalized: list[ASTNormal] = []
		child_indexs: list[int] = []
		if isinstance(tree.children[0], ASTTree) and len(tree.children[0].children) == 2:
			receiver = serializer.normalize(tree.children[0].children[0], seq)
			key = serializer.normalize(tree.children[0].children[1], receiver[-1].index + 1)
			normalized = [*receiver, *key]
			child_indexs = [receiver[-1].index, key[-1].index]
		else:
			receiver = serializer.normalize(tree.children[0], seq)
			key = ASTNormal(receiver[-1].index + 1, cls.Rules.Empty, '')
			normalized = [*receiver, key]
			child_indexs = [receiver[-1].index, key.index]

		calls_end = normalized[-1].index
		for i in range(len(tree.children) - 1):
			arg = serializer.normalize(tree.children[i + 1], calls_end + i + 1)
			normalized.extend(arg)
			child_indexs.append(arg[-1].index)

		normalized.append(ASTNormal(normalized[-1].index + 1, cls.Rules.Invoke, child_indexs))
		return normalized
