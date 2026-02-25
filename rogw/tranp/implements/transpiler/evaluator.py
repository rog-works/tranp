import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.errors import Errors
from rogw.tranp.lang.annotation import duck_typed, injectable
from rogw.tranp.semantics.procedure import Procedure
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.transpiler.types import Evaluator


class LiteralEvaluator:
	"""リテラル演算モジュール。Enum.value内のリテラル演算を対象とする想定"""

	@injectable
	def __init__(self, reflections: Reflections) -> None:
		"""インスタンスを生成

		Args:
			reflections: リフレクション @inject
		"""
		self._reflections = reflections
		self._procedure = self._build_procedure()

	def _build_procedure(self) -> Procedure[Evaluator.Value]:
		"""プロシージャーを生成

		Returns:
			プロシージャー
		"""
		procedure = Procedure[Evaluator.Value]()
		for key in LiteralEvaluator.__dict__.keys():
			if key.startswith('on_'):
				procedure.on(key, getattr(self, key))

		return procedure

	@duck_typed(Evaluator)
	def exec(self, node: Node) -> Evaluator.Value:
		"""リテラル演算の結果を出力

		Args:
			node: 基点のノード
		Returns:
			演算結果
		Raises:
			Errors.OperationNotAllowed: 許可されない演算内容
		"""
		return self._procedure.exec(node)

	def _op_bin_each(self, node: Node, elements: list[Evaluator.Value]) -> Evaluator.Value:
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
					assert self._allow_string(left) and self._allow_string(right)
					left = self._cat(left, right)
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
	
	def _allow_string(self, string: str) -> bool:
		"""文字列の書式を検証

		Args:
			string: 文字列
		Returns:
			True = 正常
		"""
		quotes = ['"', "'"]
		return len(string) >= 2 and string[0] in quotes and string[-1] in quotes
	
	def _cat(self, left: str, right: str) -> str:
		"""文字列結合

		Args:
			left: 文字列(左)
			right: 文字列(右)
		Returns:
			結合結果
		"""
		quote = left[0]
		return f'{quote}{left[1:-1]}{right[1:-1]}{quote}'

	def on_argument(self, node: defs.Argument, label: Evaluator.Value, value: Evaluator.Value) -> Evaluator.Value:
		return value

	def on_argument_label(self, node: defs.ArgumentLabel) -> Evaluator.Value:
		return node.tokens

	def on_var(self, node: defs.Var) -> Evaluator.Value:
		var_raw = self._reflections.type_of(node)
		# Enum.X = DeclLocalVar
		if var_raw.decl.is_a(defs.DeclLocalVar):
			return self.exec(var_raw.decl.parent.as_a(defs.MoveAssign).value)

		# 上記以外は全て無視して良い
		return ''

	def on_relay(self, node: defs.Relay, receiver: Evaluator.Value) -> Evaluator.Value:
		# Enum.X.value @see Py2cpp.on_relay
		if node.prop.tokens == 'value':
			receiver_raw = self._reflections.type_of(node.receiver)
			var_name = DSN.right(node.receiver.domain_name, 1)
			var_value = receiver_raw.types.as_a(defs.Enum).var_value(var_name)
			return self.exec(var_value)

		# 上記以外は全て無視して良い
		return ''

	def on_func_call(self, node: defs.FuncCall, calls: Evaluator.Value, arguments: list[Evaluator.Value]) -> Evaluator.Value:
		# スカラー型のキャストのみ許可
		org_calls = node.calls.tokens
		if org_calls == 'int':
			if isinstance(arguments[0], str):
				return int(arguments[0][1:-1])
			else:
				return int(arguments[0])
		elif org_calls == 'float':
			if isinstance(arguments[0], str):
				return float(arguments[0][1:-1])
			else:
				return float(arguments[0])
		elif org_calls == 'str':
			return f'"{str(arguments[0])}"'

		raise Errors.OperationNotAllowed(node, calls, arguments)

	def on_integer(self, node: defs.Integer) -> Evaluator.Value:
		return int(node.tokens)

	def on_float(self, node: defs.Float) -> Evaluator.Value:
		return float(node.tokens)

	def on_string(self, node: defs.String) -> Evaluator.Value:
		return node.tokens

	def on_sum(self, node: defs.Sum, elements: list[Evaluator.Value]) -> Evaluator.Value:
		return self._op_bin_each(node, elements)

	def on_term(self, node: defs.Term, elements: list[Evaluator.Value]) -> Evaluator.Value:
		return self._op_bin_each(node, elements)

	def on_factor(self, node: defs.Term, operator: Evaluator.Value, value: Evaluator.Value) -> Evaluator.Value:
		if isinstance(value, int):
			return -value if operator == '-' else value
		elif isinstance(value, float):
			return -value if operator == '-' else value
		
		raise Errors.OperationNotAllowed(node, operator, value)

	def on_group(self, node: defs.Group, expression: Evaluator.Value) -> Evaluator.Value:
		return expression

	def on_terminal(self, node: Node) -> Evaluator.Value:
		token = node.tokens
		if token in '+-*/%':
			return token

		raise Errors.OperationNotAllowed(node)

	def on_empty(self, node: defs.Empty) -> Evaluator.Value:
		# FuncCallのためEmptyを許容
		return node.tokens

	def on_fallback(self, node: Node) -> Evaluator.Value:
		raise Errors.OperationNotAllowed(node)
