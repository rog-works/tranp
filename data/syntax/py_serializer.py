from typing import cast

from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTNormal, ASTNormalizer, ASTToken, ASTTree
from rogw.tranp.lang.convertion import as_a


class PythonASTNormalizer(ASTNormalizer):
	"""AST正規化ミドルウェア(Python)"""

	class Rules:
		"""Grammarルール名"""
		# 分/ブロック
		Function = 'function'
		# 分/代入
		Move = 'move'
		# 分/行
		Break = 'break'
		Continue = 'continue'
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

	def __init__(self) -> None:
		"""インスタンスを生成"""
		super().__init__()
		self.on(self.Rules.Function, self.on_function)
		self.on(self.Rules.If, self.on_if)
		self.on(self.Rules.For, self.on_for)
		self.on(self.Rules.While, self.on_while)
		self.on(self.Rules.Ternary, self.on_ternary)
		self.on(self.Rules.OpComp, self.on_op_comp)
		self.on(self.Rules.CompOr, self.on_comp_logic)
		self.on(self.Rules.CompAnd, self.on_comp_logic)
		self.on(self.Rules.Invoke, self.on_invoke)

	def on_function(self, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(function)

		Note:
			* return: block終端へのjumpに変換
		"""
		normalized = self.normalize_tree(as_a(ASTTree, entry), seq)
		block_end = normalized[-1].child_ids[-1]
		for i, normal in enumerate(normalized):
			if normal.name == self.Rules.Return:
				normalized[i] = ASTNormal(normal.index, self.Rules.Jump, block_end)

		return normalized

	def on_if(self, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(if)

		Note:
			```
			* when: 各ブロックの先頭に移動
			* then/else: 直前の結果を評価する条件ジャンプに変換
			* block: 各ブロックの末尾に移動。ifブロック外へのjumpに変換
			```
		"""
		tree = as_a(ASTTree, entry)
		thens: list[list[ASTNormal]] = []
		then_seq = seq
		for child in cast(list[ASTTree], tree.children):
			if child.name == self.Rules.Empty:
				# 空のelse
				...
			elif child.name != self.Rules.Else:
				when = self.normalize(child.children[0], then_seq)
				block = self.normalize(child.children[1], when[-1].index + 2)
				then = ASTNormal(when[-1].index + 1, child.name, block[-1].index + 1)
				thens.append([*when, then, *block])
				then_seq = then.jump_at
			else:
				block = self.normalize(child.children[0], then_seq + 1)
				a_else = ASTNormal(then_seq, child.name, block[-1].index + 1)
				thens.append([a_else, *block])
				then_seq = a_else.jump_at

		if_end = then_seq
		normalized: list[ASTNormal] = []
		for then in thens:
			block = then[-1]
			then[-1] = ASTNormal(block.index, self.Rules.Jump, if_end)
			normalized.extend(then)

		return normalized

	def on_for(self, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(for)

		Note:
			```
			* expr: 先頭に移動。イテレーター用の隠し変数('#n')へのmoveに変換
			* var_names: 中間に移動。イテレーターのnextと(3番目)、分割代入のmoveに変換(2番目)
			* block: 末尾に移動。ブロック開始へのjumpに変換
			* break/continue: jumpに変換
			```
		"""
		tree = as_a(ASTTree, entry)
		name_num = len(tree.children) - 2

		# 1.iterates
		iter_name = ASTNormal(seq, self.Rules.Name, f'#{seq}')
		iter = self.normalize(tree.children[name_num], iter_name.index + 1)
		iter_move = ASTNormal(iter[-1].index + 1, self.Rules.Move, [seq, iter[-1].index])

		# 2.var_names
		var_name_begin = iter_move.index + 1
		var_names = [self.normalize(tree.children[i], var_name_begin + i)[0] for i in range(name_num)]

		block_begin = var_names[0].index
		next_begin = var_names[-1].index + 1
		next_end = next_begin + 3

		# 5.block
		block = self.normalize(tree.children[name_num + 1], next_end + 1)
		block[-1] = ASTNormal(block[-1].index, self.Rules.Jump, block_begin)

		block_end = block[-1].index

		# 3.next
		iter_next: list[ASTNormal] = []
		iter_next.append(ASTNormal(next_begin + 0, self.Rules.Name, iter_name.string))
		iter_next.append(ASTNormal(next_begin + 1, self.Rules.Var, [next_begin + 0]))
		iter_next.append(ASTNormal(next_begin + 2, self.Rules.Next, block_end + 1))

		# 4.var_destruction
		var_name_indexs = [name.index for name in var_names]
		var_destruction = ASTNormal(next_begin + 3, self.Rules.Move, [*var_name_indexs, next_begin + 2])

		normalized = [iter_name, *iter, iter_move, *var_names, *iter_next, var_destruction, *block]
		for i, normal in enumerate(normalized):
			if normal.name == self.Rules.Break:
				normalized[i] = ASTNormal(normal.index, self.Rules.Jump, block_end + 1)
			elif normal.name == self.Rules.Continue:
				normalized[i] = ASTNormal(normal.index, self.Rules.Jump, block_begin)

		return normalized

	def on_while(self, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(while)

		Note:
			```
			* when: 先頭に移動
			* while: 2番目に移動。直前の結果を評価する条件ジャンプに変換
			* block: 末尾に移動。ブロック開始へのjumpに変換
			* break/continue: jumpに変換
			```
		"""
		tree = as_a(ASTTree, entry)
		when = self.normalize(tree.children[0], seq)
		block = self.normalize(tree.children[1], when[-1].index + 2)
		while_end = block[-1].index + 1
		a_while = ASTNormal(when[-1].index + 1, entry.name, while_end)
		block[-1] = ASTNormal(block[-1].index, self.Rules.Jump, seq)
		normalized = [*when, a_while, *block]
		for i, normal in enumerate(normalized):
			if normal.name == self.Rules.Break:
				normalized[i] = ASTNormal(normal.index, self.Rules.Jump, while_end)
			elif normal.name == self.Rules.Continue:
				normalized[i] = ASTNormal(normal.index, self.Rules.Jump, seq)

		return normalized

	def on_ternary(self, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(ternary)

		Note:
			```
			* when: 先頭に移動
			* ternary: 2番目に移動。直前の結果を評価する条件ジャンプに変換
			* left: 3番目に移動。式の終端にjumpを追加
			* right: 末尾に移動
			```
		"""
		tree = as_a(ASTTree, entry)
		when = self.normalize(tree.children[1], seq)
		left = self.normalize(tree.children[0], when[-1].index + 2)
		right = self.normalize(tree.children[2], left[-1].index + 2)
		ternary = ASTNormal(when[-1].index + 1, entry.name, right[0].index)
		jump = ASTNormal(left[-1].index + 1, self.Rules.Jump, right[-1].index + 1)
		normalized = [*when, ternary, *left, jump, *right]
		return normalized

	def on_op_comp(self, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(op_comp)

		Note:
			* op_comp_s: 演算子を結合し、1要素の文字列トークンに変換
		"""
		tree = as_a(ASTTree, entry)
		op_comp_string = ' '.join([as_a(ASTToken, child).value.string for child in tree.children])
		op_comp = ASTNormal(seq, tree.name, op_comp_string)
		return [op_comp]

	def on_comp_logic(self, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(comp_or/comp_and)

		Note:
			* 直列化した継続要素を個別の比較演算に分割。コンテキストを演算終端のジャンプインデックスに変換
		"""
		tree = as_a(ASTTree, entry)
		ops_count = int((len(tree.children) - 1) / 2)
		ops = [self.normalize(tree.children[0], seq)]
		ops_seq = ops[0][-1].index + 1
		for i in range(ops_count):
			index = i * 2 + 1
			op = self.normalize(tree.children[index + 0], ops_seq)
			right = self.normalize(tree.children[index + 1], op[-1].index + 1)
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

	def on_invoke(self, entry: ASTEntry, seq: int) -> list[ASTNormal]:
		"""ハンドラー(invoke)

		Note:
			* primary: 必ずreceiver/keyの2要素になる様に分割
		"""
		tree = as_a(ASTTree, entry)

		normalized: list[ASTNormal] = []
		child_indexs: list[int] = []
		if tree.children[0].name != self.Rules.Invoke and isinstance(tree.children[0], ASTTree) and len(tree.children[0].children) == 2:
			# invoke以外の2要素のツリーをreceiver/keyに分解
			receiver = self.normalize(tree.children[0].children[0], seq)
			key = self.normalize(tree.children[0].children[1], receiver[-1].index + 1)
			normalized = [*receiver, *key]
			child_indexs = [receiver[-1].index, key[-1].index]
		else:
			receiver = self.normalize(tree.children[0], seq)
			key = ASTNormal(receiver[-1].index + 1, self.Rules.Empty, '')
			normalized = [*receiver, key]
			child_indexs = [receiver[-1].index, key.index]

		arg_begin = normalized[-1].index + 1
		for i in range(len(tree.children) - 1):
			arg = self.normalize(tree.children[i + 1], arg_begin)
			normalized.extend(arg)
			child_indexs.append(arg[-1].index)
			arg_begin = arg[-1].index + 1

		normalized.append(ASTNormal(normalized[-1].index + 1, self.Rules.Invoke, child_indexs))
		return normalized
