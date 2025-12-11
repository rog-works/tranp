from typing import TypeAlias

import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.errors import Errors
from rogw.tranp.semantics.procedure import Procedure
from rogw.tranp.syntax.node.node import Node

Value: TypeAlias = int | float | str


class LiteralEvaluator:
	"""リテラル演算モジュール"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self._procedure = self._build_procedure()

	def _build_procedure(self) -> Procedure[Value]:
		"""プロシージャーを生成

		Returns:
			プロシージャー
		"""
		procedure = Procedure[Value]()
		for key in LiteralEvaluator.__dict__.keys():
			if key.startswith('on_'):
				procedure.on(key, getattr(self, key))

		return procedure

	def _op_bin_each(self, node: Node, elements: list[Value]) -> Value:
		"""2項演算を解決

		Args:
			node: ノード
			elements: 値リスト
		Returns:
			値
		"""
		index = 1
		left = elements[0]
		while index < len(elements):
			op = str(elements[index])
			right = elements[index + 1]
			index += 2
			try:
				if isinstance(left, float) or isinstance(right, float) or op == '/':
					left = self._calc(float(left), op, float(right))
				elif isinstance(left, int) and isinstance(right, int):
					left = int(self._calc(left, op, right))
				elif isinstance(left, str) and isinstance(right, str) and op == '+':
					quote = left[0]
					left = f'{quote}{left[1:-1]}{right[1:-1]}{quote}'
				else:
					assert False
			except AssertionError:
				raise Errors.OperationNotAllowed(node, left, op, right)

		return left

	def _calc(self, left: float, op: str, right: float) -> float:
		"""算術演算

		Args:
			left: 左オペランド
			op: 演算子
			right: 右オペランド
		Returns:
			値
		"""
		if op == '+':
			return left + right
		elif op == '-':
			return left - right
		elif op == '/':
			return left / right
		elif op == '*':
			return left * right
		elif op == '%':
			return left % right
		else:
			assert False

	def exec(self, node: Node) -> Value:
		"""リテラル演算の結果を出力

		Args:
			node: ノード
		Returns:
			演算結果
		Raises:
			Errors.OperationNotAllowed: 許可されない演算内容
		"""
		return self._procedure.exec(node)

	def on_integer(self, node: defs.Integer) -> Value:
		return int(node.tokens)

	def on_float(self, node: defs.Float) -> Value:
		return float(node.tokens)

	def on_string(self, node: defs.String) -> Value:
		return node.tokens

	def on_sum(self, node: defs.Sum, elements: list[Value]) -> Value:
		return self._op_bin_each(node, elements)

	def on_term(self, node: defs.Term, elements: list[Value]) -> Value:
		return self._op_bin_each(node, elements)

	def on_factor(self, node: defs.Term, operator: Value, value: Value) -> Value:
		if isinstance(value, int):
			return -value if operator == '-' else value
		elif isinstance(value, float):
			return -value if operator == '-' else value
		
		raise Errors.OperationNotAllowed(node, operator, value)

	def on_group(self, node: defs.Group, expression: Value) -> Value:
		return expression

	def on_fallback(self, node: Node) -> Value:
		op = node.tokens
		if op in '+-*/%':
			return op

		raise Errors.OperationNotAllowed(node)
