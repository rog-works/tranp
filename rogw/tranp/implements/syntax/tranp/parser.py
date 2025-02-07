from collections.abc import Callable, Iterator
from enum import Enum
import re
from typing import TypeAlias, override

from rogw.tranp.implements.syntax.tranp.rule import Comps, Operators, Pattern, PatternEntry, Patterns, Repeators, Roles, Rules
from rogw.tranp.implements.syntax.tranp.token import Token
from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
from rogw.tranp.implements.syntax.tranp.tokenizer import ITokenizer, Tokenizer
from rogw.tranp.lang.convertion import as_a


class Triggers(Enum):
	"""トリガー"""
	Empty = 0
	Lookup = 1
	Step = 2
	Done = 3
	Abort = 4


class States(Enum):
	"""ステート"""
	Ready = 0
	Idle = 1
	Finish = 2
	Fail = 3


class StateMachine:
	"""ステートマシン"""

	def __init__(self, initial: States, transitions: dict[tuple[Triggers, States], States]) -> None:
		"""インスタンスを生成

		Args:
			initial: 初期ステート
			transitions: 遷移テーブル
		"""
		self.state = initial
		self.transitions = transitions
		self.handlers: dict[tuple[Triggers, States], Callable[[], None]] = {}

	def notify(self, trigger: Triggers) -> None:
		"""イベント通知

		Args:
			trigger: トリガー
		"""
		self._process(trigger)

	def _process(self, trigger: Triggers) -> None:
		"""イベント処理

		Args:
			trigger: トリガー
		"""
		key = (trigger, self.state)
		if key in self.transitions:
			self.state = self.transitions[key]

		if key in self.handlers:
			self.handlers[key]()

	def on(self, trigger: Triggers, state: States, callback: Callable[[], None]) -> None:
		"""イベントハンドラーの登録

		Args:
			trigger: トリガー
			state: ステート
			callback: ハンドラー
		"""
		key = (trigger, state)
		self.handlers[key] = callback

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}[{self.state.name}]: at {hex(id(self)).upper()}>'


StateOf: TypeAlias = Callable[[str, States], bool]


class Context:
	"""解析コンテキスト"""

	def __init__(self, cursor: int) -> None:
		"""インスタンスを生成

		Args:
			cursor: 参照位置
		"""
		self.cursor = cursor

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}: #{self.cursor} at {hex(id(self)).upper()}>'


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
			if pattern.role == Roles.Terminal:
				return ExpressionTerminal(pattern)
			else:
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

	def watches(self, context: Context) -> list[str]:
		"""参照シンボルを取得

		Args:
			context: 解析コンテキスト
		Returns:
			参照シンボルリスト
		"""
		assert False, 'Not implemented'

	def step(self, context: Context, token: Token) -> Triggers:
		"""トークンの読み出し

		Args:
			context: 解析コンテキスト
			token: Token
		Returns:
			トリガー
		"""
		assert False, 'Not implemented'

	def accept(self, context: Context, state_of: StateOf) -> Triggers:
		"""参照シンボルの状態を受け入れ

		Args:
			context: 解析コンテキスト
			state_of: 状態確認ハンドラー
		Returns:
			トリガー
		"""
		assert False, 'Not implemented'

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}: with {self._pattern.__repr__()}>'


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
		return Context(context.cursor - offset)

	def _handle_result(self, index: int, trigger: Triggers) -> Triggers:
		if trigger == Triggers.Done:
			return Triggers.Done if index == len(self._expressions) - 1 else Triggers.Step
		elif trigger == Triggers.Abort:
			return Triggers.Abort
		else:
			return Triggers.Empty


class ExpressionsRepeat(Expressions):
	"""式(グループ/繰り返し)"""

	def __init__(self, pattern: PatternEntry) -> None:
		assert len(as_a(Patterns, pattern).entries) == 1
		super().__init__(pattern)
		self._repeats = 0

	@property
	def _as_patterns(self) -> Patterns:
		return as_a(Patterns, self._pattern)

	@override
	def watches(self, context: Context) -> list[str]:
		return self._expressions[0].watches(context)

	@override
	def step(self, context: Context, token: Token) -> Triggers:
		return self._handle_result(self._expressions[0].step(context, token))

	@override
	def accept(self, context: Context, state_of: StateOf) -> Triggers:
		return self._handle_result(self._expressions[0].accept(context, state_of))

	def _handle_result(self, trigger: Triggers) -> Triggers:
		patterns = self._as_patterns
		if trigger == Triggers.Abort:
			if patterns.rep != Repeators.OverOne:
				self._repeats = 0
				return Triggers.Done
			elif self._repeats >= 1:
				self._repeats = 0
				return Triggers.Done
		elif trigger == Triggers.Done:
			if patterns.rep in [Repeators.OneOrZero, Repeators.OneOrEmpty]:
				self._repeats = 0
				return Triggers.Done
			else:
				self._repeats += 1
				return Triggers.Step

		return trigger


class Task:
	"""タスク"""

	def __init__(self, name: str, pattern: PatternEntry) -> None:
		"""インスタンスを生成

		Args:
			name: シンボル名
			pattern: マッチパターンエントリー
		"""
		self._name = name
		self._expression = Expression.factory(pattern)
		self._cursor = 0
		self._states = StateMachine(States.Ready, {
			(Triggers.Lookup, States.Ready): States.Idle,
			(Triggers.Done, States.Idle): States.Finish,
			(Triggers.Abort, States.Idle): States.Fail,
			(Triggers.Lookup, States.Finish): States.Idle,
			(Triggers.Done, States.Finish): States.Ready,
			(Triggers.Lookup, States.Fail): States.Idle,
			(Triggers.Done, States.Fail): States.Ready,
		})
		self._states.on(Triggers.Step, States.Idle, lambda: self._cursor_step())
		self._states.on(Triggers.Done, States.Idle, lambda: self._cursor_reset())
		self._states.on(Triggers.Abort, States.Idle, lambda: self._cursor_reset())

	@property
	def name(self) -> str:
		"""Returns: シンボル名"""
		return self._name

	def state_of(self, expect: States) -> bool:
		"""状態を確認

		Args:
			expect: 判定する状態
		Returns:
			True = 一致
		"""
		return self._states.state == expect

	def notify(self, trigger: Triggers) -> None:
		"""イベント通知

		Args:
			trigger: トリガー
		"""
		self._states.notify(trigger)

	def lookup(self, on: bool) -> None:
		"""ルックアップ

		Args:
			on: True = ルックアップ
		"""
		self.notify(Triggers.Lookup if on else Triggers.Done)

	def watches(self) -> list[str]:
		"""Returns: 参照シンボルリスト"""
		return self._expression.watches(self._new_context())

	def step(self, token: Token) -> None:
		"""トークンの読み出し

		Args:
			token: トークン
		"""
		self.notify(self._expression.step(self._new_context(), token))

	def accept(self, state_of: StateOf) -> None:
		"""参照シンボルの状態を受け入れ

		Args:
			context: 解析コンテキスト
			state_of: 状態確認ハンドラー
		"""
		self.notify(self._expression.accept(self._new_context(), state_of))

	def _cursor_step(self) -> None:
		"""カーソルを1つ進行"""
		self._cursor += 1

	def _cursor_reset(self) -> None:
		"""カーソルを初期化"""
		self._cursor = 0

	def _new_context(self) -> Context:
		"""Returns: 解析コンテキスト"""
		return Context(self._cursor)

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}["{self.name}"]: {self._states.state.name} #{self._cursor}>'


class SyntaxParser:
	"""シンタックスパーサー"""

	def __init__(self, rules: Rules, tokenizer: ITokenizer | None = None) -> None:
		"""インスタンスを生成

		Args:
			rules: ルールリスト
			tokenizer: トークンパーサー (default = None)
		"""
		self.rules = rules
		self.tokenizer = tokenizer if tokenizer else Tokenizer()

	def parse(self, source: str, entrypoint: str) -> Iterator[ASTEntry]:
		"""ソースコードを解析してASTを生成

		Args:
			source: ソースコード
			entrypoint: 基点のシンボル名
		Returns:
			ASTエントリー
		"""
		tokens = self.tokenizer.parse(source)
		return self._parse(self.new_tasks(), tokens, entrypoint)

	def new_tasks(self) -> dict[str, Task]:
		"""タスク一覧を生成

		Args:
			タスク一覧
		"""
		return {name: Task(name, pattern) for name, pattern in self.rules.items()}

	def _parse(self, tasks: dict[str, Task], tokens: list[Token], entrypoint: str) -> Iterator[ASTEntry]:
		"""ソースコードを解析してASTを生成

		Args:
			tasks: タスク一覧
			tokens: トークンリスト
			entrypoint: 基点のシンボル名
		Returns:
			ASTエントリーのイテレーター
		"""
		index = 0
		entries: list[ASTEntry] = []
		while index < len(tokens):
			names = self.lookup(tasks, entrypoint)
			finish_names = self.step(tasks, tokens[index], names)
			finish_names = self.accept(tasks, names, finish_names)
			# FIXME トークンを1文字以上読んだ事が正しい進行条件
			if len(finish_names) == 0:
				continue

			ast, entries = self.stack(tokens[index], entries.copy(), finish_names)
			yield ast
			index += 1

	def lookup(self, tasks: dict[str, Task], entrypoint: str) -> list[str]:
		"""基点のシンボルから処理対象のシンボルを再帰的にルックアップ

		Args:
			tasks: タスク一覧
			entrypoint: 基点のシンボル名
		Returns:
			シンボルリスト(処理対象)
		"""
		lookup_names = {entrypoint: True}
		stack_names = list(lookup_names.keys())
		while len(stack_names) > 0:
			name = stack_names.pop(0)
			candidate_names = tasks[name].watches()
			add_names = {name: True for name in candidate_names if name not in lookup_names}
			lookup_names.update(add_names)
			stack_names.extend(add_names.keys())

		for name, task in tasks.items():
			task.lookup(name in lookup_names)

		return [name for name in lookup_names.keys() if tasks[name].state_of(States.Idle)]

	def step(self, tasks: dict[str, Task], token: Token, names: list[str]) -> list[str]:
		"""トークンを読み出し、完了したシンボルを抽出

		Args:
			tasks: タスク一覧
			token: トークン
			names: シンボルリスト(処理対象)
		Returns:
			シンボルリスト(処理完了)
		"""
		for name in names:
			tasks[name].step(token)

		return [name for name in names if tasks[name].state_of(States.Finish)]

	def accept(self, tasks: dict[str, Task], names: list[str], finish_names: list[str]) -> list[str]:
		"""参照シンボルの状態を受け入れ、完了したシンボルを抽出

		Args:
			tasks: タスク一覧
			names: シンボルリスト(処理対象)
			finish_names: シンボルリスト(処理完了)
		Returns:
			シンボルリスト(処理完了)
		"""
		new_finish_names = finish_names.copy()
		while True:
			accept_names = [name for name in names if tasks[name].state_of(States.Idle)]
			for name in accept_names:
				tasks[name].accept(lambda name, state: tasks[name].state_of(state))

			add_finish_names = [name for name in accept_names if tasks[name].state_of(States.Finish)]
			if len(add_finish_names) == 0:
				break

			new_finish_names.extend(add_finish_names)

		return new_finish_names

	def stack(self, token: Token, entries: list[ASTEntry], finish_names: list[str]) -> tuple[ASTEntry, list[ASTEntry]]:
		"""今回解析した結果からASTを生成し、以前のASTを内部にスタック

		Args:
			token: トークン
			entries: ASTエントリーリスト(以前)
			names: シンボルリスト(処理完了)
		Returns:
			(ASTエントリー, ASTエントリーリスト(新))
		"""
		ast: ASTEntry = ASTToken.empty()
		for name in finish_names:
			if name not in self.rules:
				ast = ASTToken(token.type.name, token)
				entries.append(ast)
				continue

			pattern = self.rules[name]
			if isinstance(pattern, Pattern) and pattern.role == Roles.Terminal:
				ast = ASTToken(name, token)
				entries.append(ast)
			else:
				ast = ASTTree(name, entries)
				entries = [ast]

		return ast, entries
