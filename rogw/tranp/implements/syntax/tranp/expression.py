import re
from typing import override

from rogw.tranp.implements.syntax.tranp.rule import Comps, Operators, Pattern, PatternEntry, Patterns, Repeators
from rogw.tranp.implements.syntax.tranp.state import Context, DoneReasons, State, StateOf, States, Trigger, Triggers
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
		elif pattern.rep != Repeators.NoRepeat:
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

	def step(self, context: Context, token: Token) -> Trigger:
		"""トークンの読み出しイベント。進行に応じたトリガーを返却

		Args:
			context: 解析コンテキスト
			token: トークン
		Returns:
			トリガー
		"""
		assert False, 'Not implemented'

	def accept(self, context: Context, state_of: StateOf) -> Trigger:
		"""シンボル更新イベント。進行に応じたトリガーを返却

		Args:
			context: 解析コンテキスト
			state_of: 状態確認ハンドラー
		Returns:
			トリガー
		"""
		assert False, 'Not implemented'


class ExpressionTerminal(Expression):
	"""式(終端記号)"""

	@property
	def _as_pattern(self) -> Pattern:
		return as_a(Pattern, self._pattern)

	@override
	def watches(self, context: Context) -> list[str]:
		return []

	@override
	def step(self, context: Context, token: Token) -> Trigger:
		if context.cursor != 0:
			return Triggers.Empty

		pattern = self._as_pattern
		ok = False
		if pattern.comp == Comps.Regexp:
			ok = re.fullmatch(pattern.expression[1:-1], token.string) is not None
		else:
			ok = pattern.expression[1:-1] == token.string

		return Triggers.FinishStep if ok else Triggers.Abort

	@override
	def accept(self, context: Context, state_of: StateOf) -> Trigger:
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
	def step(self, context: Context, token: Token) -> Trigger:
		return Triggers.Empty

	@override
	def accept(self, context: Context, state_of: StateOf) -> Trigger:
		if context.cursor != 0:
			return Triggers.Empty

		if not state_of(self._as_pattern.expression, States.Done):
			return Triggers.Empty

		to_trigger = {
			States.FinishStep: Triggers.FinishStep,
			States.FinishSkip: Triggers.FinishSkip,
			States.UnfinishStep: Triggers.UnfinishStep,
			States.UnfinishSkip: Triggers.UnfinishSkip,
			States.Abort: Triggers.Abort,
		}
		trigger = [trigger for state, trigger in to_trigger.items() if state_of(self._as_pattern.expression, state)].pop()
		return trigger


class Expressions(Expression):
	"""式(グループ/基底)"""

	def __init__(self, pattern: PatternEntry) -> None:
		super().__init__(pattern)
		self._expressions = [Expression.factory(pattern) for pattern in as_a(Patterns, pattern)]

	def _group_states(self, context: Context) -> tuple[list[State], list[int]]:
		datum = context.datum(self)
		if len(datum.group_states) == 0:
			for _ in range(len(self._expressions)):
				datum.group_states.append(States.Idle)

		return datum.group_states, datum.resolve_orders


class ExpressionsOr(Expressions):
	"""式(グループ/Or)"""

	@override
	def watches(self, context: Context) -> list[str]:
		symbols: list[str] = []
		for expression in self._expressions:
			symbols.extend(expression.watches(context))

		return symbols

	@override
	def step(self, context: Context, token: Token) -> Trigger:
		group_states, resolve_orders = self._group_states(context)
		for index, expression in enumerate(self._expressions):
			if group_states[index] == States.Done:
				continue

			group_states[index] = State.from_trigger(expression.step(context, token))
			if group_states[index] == States.Done:
				resolve_orders.append(index)

		return self._to_trigger(group_states, resolve_orders)

	@override
	def accept(self, context: Context, state_of: StateOf) -> Trigger:
		group_states, resolve_orders = self._group_states(context)
		for index, expression in enumerate(self._expressions):
			if group_states[index] == States.Done:
				continue

			group_states[index] = State.from_trigger(expression.accept(context, state_of))
			if group_states[index] == States.Done:
				resolve_orders.append(index)

		return self._to_trigger(group_states, resolve_orders)

	def _to_trigger(self, group_states: list[State], resolve_orders: list[int]) -> Trigger:
		if len([True for state in group_states if state != States.Done]) > 0:
			return Triggers.Empty

		assert len(group_states) == len(resolve_orders), 'Never'

		last = group_states[resolve_orders[-1]]
		unfinish = len([True for state in group_states if state.reason.unfinish]) > 0
		if unfinish:
			return Triggers.UnfinishStep if last.reason.physically else Triggers.UnfinishSkip
		else:
			return Triggers.FinishStep if last.reason.physically else Triggers.FinishSkip


class ExpressionsAnd(Expressions):
	"""式(グループ/And)"""

	@override
	def watches(self, context: Context) -> list[str]:
		symbols: list[str] = []
		for index, expression in enumerate(self._expressions):
			in_context = self._new_context(context, index)
			symbols.extend(expression.watches(in_context))

		return symbols

	@override
	def step(self, context: Context, token: Token) -> Trigger:
		group_states, _ = self._group_states(context)
		for index, expression in enumerate(self._expressions):
			in_context = self._new_context(context, index)
			if group_states[index] != States.Done and in_context.cursor == 0:
				group_states[index] = State.from_trigger(expression.step(in_context, token))

		begin_context = self._new_context(context, 0)
		return self._to_trigger(group_states, begin_context.cursor)

	@override
	def accept(self, context: Context, state_of: StateOf) -> Trigger:
		group_states, _ = self._group_states(context)
		for index, expression in enumerate(self._expressions):
			in_context = self._new_context(context, index)
			if group_states[index] != States.Done and in_context.cursor == 0:
				group_states[index] = State.from_trigger(expression.accept(in_context, state_of))

		begin_context = self._new_context(context, 0)
		return self._to_trigger(group_states, begin_context.cursor)

	def _new_context(self, context: Context, offset: int) -> Context:
		cursor = context.cursor - offset
		if context.repeat and cursor >= 0:
			return context.to_and(cursor % len(self._expressions))
		else:
			return context.to_and(cursor)

	def _to_trigger(self, group_states: list[State], cursor: int) -> Trigger:
		if cursor < 0 or cursor >= len(self._expressions):
			return Triggers.Empty

		peek = group_states[cursor]
		if peek != States.Done:
			return Triggers.Empty

		if cursor < len(self._expressions) - 1:
			return Triggers.Step if peek.reason.physically else Triggers.Skip

		unfinish = len([True for in_state in group_states if in_state.reason.unfinish]) > 0
		if unfinish:
			return Triggers.UnfinishStep if peek.reason.physically else Triggers.UnfinishSkip
		else:
			return Triggers.FinishStep if peek.reason.physically else Triggers.FinishSkip


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
	def step(self, context: Context, token: Token) -> Trigger:
		trigger = self._expressions[0].step(context.to_repeat(self._repeated), token)
		return self._handle_result(context, trigger)

	@override
	def accept(self, context: Context, state_of: StateOf) -> Trigger:
		trigger = self._expressions[0].accept(context.to_repeat(self._repeated), state_of)
		return self._handle_result(context, trigger)

	def _handle_result(self, context: Context, trigger: Trigger) -> Trigger:
		peek = State.from_trigger(trigger)
		if peek != States.Done:
			return Triggers.Empty

		assert not peek.reason.unfinish, 'Must be Finish or Abort'

		group_states = context.datum(self).group_states
		group_states.append(peek)

		patterns = self._as_patterns
		if peek.reason == DoneReasons.Abort:
			if len(group_states) == 0:
				return Triggers.Abort if patterns.rep == Repeators.OverOne else Triggers.FinishSkip
			else:
				# FIXME 文字数カウントを考慮するべきなのか不明
				last = group_states[-1]
				return Triggers.FinishStep if last.reason.physically else Triggers.FinishSkip
		else:
			if len(group_states) == 1 and patterns.rep in [Repeators.OneOrZero, Repeators.OneOrEmpty]:
				return Triggers.FinishStep if peek.reason.physically else Triggers.FinishSkip
			else:
				return Triggers.Step if peek.reason.physically else Triggers.Skip
