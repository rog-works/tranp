import re
from typing import override

from rogw.tranp.implements.syntax.tranp.rule import Comps, Operators, Pattern, PatternEntry, Patterns, Repeators
from rogw.tranp.implements.syntax.tranp.state import Context, DoneReasons, StateStore, State, StateOf, States, Trigger, Triggers
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

	def step(self, context: Context, token_no: int, token: Token) -> Trigger:
		"""トークンの読み出しイベント。進行に応じたトリガーを返却

		Args:
			context: 解析コンテキスト
			token_no: トークンNo
			token: トークン
		Returns:
			トリガー
		"""
		assert False, 'Not implemented'

	def accept(self, context: Context, token_no: int, state_of: StateOf) -> Trigger:
		"""シンボル更新イベント。進行に応じたトリガーを返却

		Args:
			context: 解析コンテキスト
			token_no: トークンNo
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
	def step(self, context: Context, token_no: int, token: Token) -> Trigger:
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
	def accept(self, context: Context, token_no: int, state_of: StateOf) -> Trigger:
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
	def step(self, context: Context, token_no: int, token: Token) -> Trigger:
		return Triggers.Empty

	@override
	def accept(self, context: Context, token_no: int, state_of: StateOf) -> Trigger:
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

	def _state_stores(self, context: Context) -> list[StateStore]:
		store = context.store_by(self)
		if len(store.state_stores) == 0:
			for _ in range(len(self._expressions)):
				store.state_stores.append(StateStore())

		return store.state_stores


class ExpressionsOr(Expressions):
	"""式(グループ/Or)"""

	@override
	def watches(self, context: Context) -> list[str]:
		symbols: list[str] = []
		for expression in self._expressions:
			symbols.extend(expression.watches(context))

		return symbols

	@override
	def step(self, context: Context, token_no: int, token: Token) -> Trigger:
		state_stores = self._state_stores(context)
		for index, expression in enumerate(self._expressions):
			state_store = state_stores[index]
			if state_store.state != States.Done:
				state_store.state = States.from_trigger(expression.step(context, token_no, token))
				state_store.order = len([True for state_store in state_stores if state_store.state == States.Done]) - 1
				state_store.token_no = token_no

		return self._to_trigger(token_no, state_stores)

	@override
	def accept(self, context: Context, token_no: int, state_of: StateOf) -> Trigger:
		state_stores = self._state_stores(context)
		for index, expression in enumerate(self._expressions):
			state_store = state_stores[index]
			if state_store.state != States.Done:
				state_store.state = States.from_trigger(expression.accept(context, token_no, state_of))
				state_store.order = len([True for state_store in state_stores if state_store.state == States.Done]) - 1
				state_store.token_no = token_no

		return self._to_trigger(token_no, state_stores)

	def _to_trigger(self, token_no: int, state_stores: list[StateStore]) -> Trigger:
		# 終了無し
		done_num = len([True for state_store in state_stores if state_store.state == States.Done])
		if done_num == 0:
			return Triggers.Empty

		# 全て失敗
		abort_num = len([True for state_store in state_stores if state_store.state == States.Abort])
		if abort_num == len(self._expressions):
			return Triggers.Abort

		# 成功無し
		succeeded = {state_store.order: state_store for state_store in state_stores if state_store.state == States.Done and state_store.state != States.Abort}
		if len(succeeded) == 0:
			return Triggers.Empty

		# 未決定の条件が存在、または最新の結果が部分適合の場合は部分適合
		stay_num = len(self._expressions) - done_num
		_, last_store = sorted(succeeded.items(), key=lambda entry: entry[0]).pop()
		physically = last_store.token_no == token_no and last_store.state.reason.physically
		if stay_num > 0 or last_store.state.reason.unfinish:
			return Triggers.UnfinishStep if physically else Triggers.UnfinishSkip

		# 最新の結果が完了
		return Triggers.FinishStep if physically else Triggers.FinishSkip


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
	def step(self, context: Context, token_no: int, token: Token) -> Trigger:
		state_stores = self._state_stores(context)
		for index, expression in enumerate(self._expressions):
			in_context = self._new_context(context, index)
			state_store = state_stores[index]
			if state_store.state != States.Done and in_context.cursor == 0:
				state_store.state = States.from_trigger(expression.step(in_context, token_no, token))
				state_store.order = index
				state_store.token_no = token_no

		begin_context = self._new_context(context, 0)
		return self._to_trigger(token_no, state_stores, begin_context.cursor)

	@override
	def accept(self, context: Context, token_no: int, state_of: StateOf) -> Trigger:
		state_stores = self._state_stores(context)
		for index, expression in enumerate(self._expressions):
			in_context = self._new_context(context, index)
			state_store = state_stores[index]
			if state_store.state != States.Done and in_context.cursor == 0:
				state_store.state = States.from_trigger(expression.accept(in_context, token_no, state_of))
				state_store.order = index
				state_store.token_no = token_no

		begin_context = self._new_context(context, 0)
		return self._to_trigger(token_no, state_stores, begin_context.cursor)

	def _new_context(self, context: Context, offset: int) -> Context:
		cursor = context.cursor - offset
		if context.repeat and cursor >= 0:
			return context.to_and(cursor % len(self._expressions))
		else:
			return context.to_and(cursor)

	def _to_trigger(self, token_no: int, state_stores: list[StateStore], offset: int) -> Trigger:
		# 範囲外
		if offset < 0 or offset >= len(self._expressions):
			return Triggers.Empty

		# 最新の結果。失敗は即座に失敗。終了していない場合は無し
		peek_store = [state_store for state_store in state_stores if state_store.order != -1].pop()
		if peek_store.state == States.Abort:
			return Triggers.Abort
		elif peek_store.state != States.Done:
			return Triggers.Empty

		# 途中の条件。結果に拘わらず進行のみ
		if offset < len(self._expressions) - 1:
			return Triggers.Step if peek_store.state.reason.physically else Triggers.Skip

		# 最後の条件。部分適合を含む場合は部分適合。それ以外は完了
		last_store = peek_store
		unfinish = len([True for state_store in state_stores if state_store.state.reason.unfinish]) > 0
		physically = last_store.token_no == token_no and last_store.state.reason.physically
		if unfinish:
			return Triggers.UnfinishStep if physically else Triggers.UnfinishSkip
		else:
			return Triggers.FinishStep if physically else Triggers.FinishSkip


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
	def step(self, context: Context, token_no: int, token: Token) -> Trigger:
		in_context = context.to_repeat(self._repeated)
		trigger = self._expressions[0].step(in_context, token_no, token)
		return self._to_trigger(token_no, context.store_by(self).state_stores, trigger)

	@override
	def accept(self, context: Context, token_no: int, state_of: StateOf) -> Trigger:
		in_context = context.to_repeat(self._repeated)
		trigger = self._expressions[0].accept(in_context, token_no, state_of)
		return self._to_trigger(token_no, context.store_by(self).state_stores, trigger)

	def _to_trigger(self, token_no: int, state_stores: list[StateStore], trigger: Trigger) -> Trigger:
		state = States.from_trigger(trigger)
		if state != States.Done:
			return Triggers.Empty

		assert not state.reason.unfinish, f'Must be Finish or Abort, state: {state}'

		if state != States.Abort:
			state_store = StateStore(state)
			state_store.token_no = token_no
			state_stores.append(state_store)

		patterns = self._as_patterns
		if state == States.Abort:
			if len(state_stores) == 0:
				return Triggers.Abort if patterns.rep == Repeators.OverOne else Triggers.FinishSkip
			else:
				last_store = state_stores[-1]
				physically = last_store.token_no == token_no and last_store.state.reason.physically
				return Triggers.FinishStep if physically else Triggers.FinishSkip
		else:
			last_store = state_stores[-1]
			physically = last_store.token_no == token_no and last_store.state.reason.physically
			if len(state_stores) == 1 and patterns.rep in [Repeators.OneOrZero, Repeators.OneOrEmpty]:
				return Triggers.FinishStep if physically else Triggers.FinishSkip
			else:
				return Triggers.Step if physically else Triggers.Skip
