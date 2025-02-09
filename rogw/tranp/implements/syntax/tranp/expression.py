import re
from typing import override

from rogw.tranp.implements.syntax.tranp.rule import Comps, Operators, Pattern, PatternEntry, Patterns, Repeators
from rogw.tranp.implements.syntax.tranp.state import Context, StateOf, States, Triggers
from rogw.tranp.implements.syntax.tranp.token import Token
from rogw.tranp.lang.convertion import as_a


class Expression:
	"""式(基底)"""

	@classmethod
	def factory(cls, pattern: PatternEntry) -> 'Expression':
		"""マッチパターンに応じた式インスタンスを生成

		Args:
			pattern: マッチパターンエントリー
		Returns:
			インスタンス
		"""
		if isinstance(pattern, Pattern):
			return ExpressionSymbol(pattern)
		else:
			if pattern.rep != Repeators.NoRepeat:
				return ExpressionsRepeat(pattern)
			elif pattern.op == Operators.Or:
				return ExpressionsOr(pattern)
			else:
				return ExpressionsAnd(pattern)

	def __init__(self, pattern: PatternEntry) -> None:
		"""インスタンスを生成

		Args:
			pattern: マッチパターンエントリー
		"""
		self._pattern = pattern

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}: with {self._pattern.__repr__()}>'

	def watches(self, context: Context) -> list[str]:
		"""現在の参照位置を基に参照中のシンボルリストを返却

		Args:
			context: 解析コンテキスト
		Returns:
			シンボルリスト
		"""
		assert False, 'Not implemented'

	def step(self, context: Context, token: Token) -> Triggers:
		"""トークンの読み出しイベント。進行に応じたトリガーを返却

		Args:
			context: 解析コンテキスト
			token: トークン
		Returns:
			トリガー
		"""
		assert False, 'Not implemented'

	def accept(self, context: Context, state_of: StateOf) -> Triggers:
		"""シンボル更新イベント。進行に応じたトリガーを返却

		Args:
			context: 解析コンテキスト
			state_of: 状態確認ハンドラー
		Returns:
			トリガー
		"""
		assert False, 'Not implemented'


class Expressions(Expression):
	"""式(グループ/基底)"""

	def __init__(self, pattern: PatternEntry) -> None:
		super().__init__(pattern)
		self._expressions = [Expression.factory(pattern) for pattern in as_a(Patterns, pattern)]


class ExpressionTerminal(Expression):
	"""式(終端記号)"""

	@property
	def _as_pattern(self) -> Pattern:
		return as_a(Pattern, self._pattern)

	@override
	def watches(self, context: Context) -> list[str]:
		return []

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		if context.cursor != 0:
			return Triggers.Empty

		pattern = self._as_pattern
		ok = False
		if pattern.comp == Comps.Regexp:
			ok = re.fullmatch(pattern.expression[1:-1], token.string) is not None
		else:
			ok = pattern.expression[1:-1] == token.string

		return Triggers.Done if ok else Triggers.Abort

	@override
	def accept(self, context: Context, state_of: StateOf) -> Triggers:
		return Triggers.Empty


class ExpressionSymbol(Expression):
	"""式(非終端記号)"""

	@property
	def _as_pattern(self) -> Pattern:
		return as_a(Pattern, self._pattern)

	@override
	def watches(self, context: Context) -> list[str]:
		return [self._as_pattern.expression] if context.cursor == 0 else []

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		return Triggers.Empty

	@override
	def accept(self, context: Context, state_of: StateOf) -> Triggers:
		if context.cursor != 0:
			return Triggers.Empty
		elif state_of(self._as_pattern.expression, States.Finish):
			return Triggers.Done
		elif state_of(self._as_pattern.expression, States.Fail):
			return Triggers.Abort
		else:
			return Triggers.Empty


class ExpressionsOr(Expressions):
	"""式(グループ/Or)"""

	@override
	def watches(self, context: Context) -> list[str]:
		symbols: list[str] = []
		for expression in self._expressions:
			symbols.extend(expression.watches(context))

		return symbols

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		return self._select_trigger([expression.step(context, token) for expression in self._expressions])

	@override
	def accept(self, context: Context, state_of: StateOf) -> Triggers:
		return self._select_trigger([expression.accept(context, state_of) for expression in self._expressions])

	def _select_trigger(self, triggers: list[Triggers]) -> Triggers:
		priorities = [Triggers.Done, Triggers.Step, Triggers.Empty]
		for expect in priorities:
			if expect in triggers:
				return expect

		return Triggers.Abort


class ExpressionsAnd(Expressions):
	"""式(グループ/And)"""

	@override
	def watches(self, context: Context) -> list[str]:
		symbols: list[str] = []
		for index, expression in enumerate(self._expressions):
			symbols.extend(expression.watches(self._new_context(context, index)))

		return symbols

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		for index, expression in enumerate(self._expressions):
			trigger = self._handle_result(index, expression.step(self._new_context(context, index), token))
			if trigger != Triggers.Empty:
				return trigger

		return Triggers.Empty

	@override
	def accept(self, context: Context, state_of: StateOf) -> Triggers:
		for index, expression in enumerate(self._expressions):
			trigger = self._handle_result(index, expression.accept(self._new_context(context, index), state_of))
			if trigger != Triggers.Empty:
				return trigger

		return Triggers.Empty

	def _new_context(self, context: Context, offset: int) -> Context:
		cursor = context.cursor - offset
		if context.repeat and cursor >= 0:
			return context.to_and(cursor % len(self._expressions))
		else:
			return context.to_and(cursor)

	def _handle_result(self, index: int, trigger: Triggers) -> Triggers:
		if trigger == Triggers.Done:
			return Triggers.Done if index == len(self._expressions) - 1 else Triggers.Step
		elif trigger == Triggers.Abort:
			return Triggers.Abort
		else:
			return Triggers.Empty


class ExpressionsRepeat(Expressions):
	"""式(グループ/繰り返し)"""

	@property
	def _as_patterns(self) -> Patterns:
		return as_a(Patterns, self._pattern)

	@property
	def _repeated(self) -> bool:
		return self._as_patterns.rep != Repeators.NoRepeat

	@override
	def watches(self, context: Context) -> list[str]:
		return self._expressions[0].watches(context.to_repeat(self._repeated))

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		return self._handle_result(context, self._expressions[0].step(context.to_repeat(self._repeated), token))

	@override
	def accept(self, context: Context, state_of: StateOf) -> Triggers:
		return self._handle_result(context, self._expressions[0].accept(context.to_repeat(self._repeated), state_of))

	def _handle_result(self, context: Context, trigger: Triggers) -> Triggers:
		patterns = self._as_patterns
		if trigger == Triggers.Abort:
			if patterns.rep != Repeators.OverOne:
				context.datum(self).repeats = 0
				return Triggers.Done
			elif context.datum(self).repeats >= 1:
				context.datum(self).repeats = 0
				return Triggers.Done
		elif trigger == Triggers.Done:
			if patterns.rep in [Repeators.OneOrZero, Repeators.OneOrEmpty]:
				context.datum(self).repeats = 0
				return Triggers.Done
			else:
				context.datum(self).repeats += 1
				return Triggers.Step

		return trigger
