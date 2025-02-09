from collections.abc import Callable, Iterator, Mapping, ValuesView
from enum import Enum
import re
from typing import KeysView, TypeAlias, override

from rogw.tranp.implements.syntax.tranp.rule import Comps, Operators, Pattern, PatternEntry, Patterns, Repeators, Roles, Rules, Unwraps
from rogw.tranp.implements.syntax.tranp.token import Token
from rogw.tranp.implements.syntax.tranp.ast import ASTEntry, ASTToken, ASTTree
from rogw.tranp.implements.syntax.tranp.tokenizer import ITokenizer, Tokenizer
from rogw.tranp.lang.convertion import as_a
from rogw.tranp.lang.sequence import flatten


class Triggers(Enum):
	"""トリガー"""
	Wakeup = 0
	Sleep = 1
	Step = 10
	Done = 11
	Abort = 12
	Empty = 13


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

	def __init__(self, cursor: int, repeat: bool = False) -> None:
		"""インスタンスを生成

		Args:
			cursor: 参照位置
		"""
		self.cursor = cursor
		self.repeat = repeat

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

	def reset(self) -> None:
		...


class Expressions(Expression):
	"""式(グループ/基底)"""

	def __init__(self, pattern: PatternEntry) -> None:
		super().__init__(pattern)
		self._expressions = [Expression.factory(pattern) for pattern in as_a(Patterns, pattern)]

	@override
	def reset(self) -> None:
		for expression in self._expressions:
			expression.reset()


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
			return Context(cursor % len(self._expressions))
		else:
			return Context(cursor)

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
		return self._handle_result(self._expressions[0].step(self._new_context(context), token))

	@override
	def accept(self, context: Context, state_of: StateOf) -> Triggers:
		return self._handle_result(self._expressions[0].accept(self._new_context(context), state_of))

	@override
	def reset(self) -> None:
		super().reset()
		self._repeats = 0

	def _new_context(self, context: Context) -> Context:
		return Context(context.cursor, self._as_patterns.rep != Repeators.NoRepeat)

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

	def __init__(self, name: str, expression: Expression) -> None:
		"""インスタンスを生成

		Args:
			name: シンボル名
			pattern: マッチパターンエントリー
		"""
		self._name = name
		self._expression = expression
		self._cursor = 0
		self._states = StateMachine(States.Ready, {
			(Triggers.Wakeup, States.Ready): States.Idle,
			(Triggers.Sleep, States.Idle): States.Ready,
			(Triggers.Done, States.Idle): States.Finish,
			(Triggers.Abort, States.Idle): States.Fail,
			(Triggers.Sleep, States.Finish): States.Ready,
			(Triggers.Wakeup, States.Finish): States.Idle,
			(Triggers.Sleep, States.Fail): States.Ready,
			(Triggers.Wakeup, States.Fail): States.Idle,
		})
		self._states.on(Triggers.Sleep, States.Idle, lambda: self._on_reset())
		self._states.on(Triggers.Step, States.Idle, lambda: self._on_step())
		self._states.on(Triggers.Done, States.Idle, lambda: self._on_reset())
		self._states.on(Triggers.Abort, States.Idle, lambda: self._on_reset())

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}[{repr(self.name)}]: {self._states.state.name} #{self._cursor}>'

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

	def wakeup(self, on: bool) -> bool:
		"""起動イベントを発火。待機状態か否かを返却

		Args:
			on: True = 起動, False = 休眠
		Returns:
			True = 待機
		"""
		self.notify(Triggers.Wakeup if on else Triggers.Sleep)
		return self.state_of(States.Idle)

	def watches(self) -> list[str]:
		"""現在の参照位置を基に参照中のシンボルリストを返却

		Returns:
			シンボルリスト
		"""
		return self._expression.watches(Context(self._cursor))

	def step(self, token: Token) -> bool:
		"""トークンの読み出しイベントを発火。状態変化を返却

		Args:
			token: トークン
		Returns:
			True = 状態が変化
		"""
		trigger = self._expression.step(Context(self._cursor), token)
		self.notify(trigger)
		return trigger != Triggers.Empty

	def accept(self, state_of: StateOf) -> bool:
		"""シンボル更新イベントを発火。状態変化を返却

		Args:
			state_of: 状態確認ハンドラー
		Returns:
			True = 状態が変化
		"""
		trigger = self._expression.accept(Context(self._cursor), state_of)
		self.notify(trigger)
		return trigger != Triggers.Empty

	def _on_step(self) -> None:
		"""進行イベントハンドラー"""
		self._cursor += 1

	def _on_reset(self) -> None:
		"""リセットイベントハンドラー"""
		self._cursor = 0
		self._expression.reset()


class Tasks(Mapping[str, Task]):
	"""タスク一覧"""

	def __init__(self, rules: Rules) -> None:
		"""インスタンスを生成

		Args:
			rules: ルール一覧
		"""
		super().__init__()
		self._tasks = self._make_tasks(rules)
		self._depends = self._make_depends(rules)

	def _make_tasks(self, rules: Rules) -> dict[str, Task]:
		"""ルールを基にタスクを生成

		Args:
			rules: ルール一覧
		Returns:
			タスク一覧
		"""
		tasks = {name: Task(name, Expression.factory(pattern)) for name, pattern in rules.items()}
		terminals = {terminal.expression: terminal for terminal in flatten([pattern.terminals() for pattern in rules.values()])}
		terminal_tasks = {name: Task(name, ExpressionTerminal(terminal)) for name, terminal in terminals.items()}
		return {**tasks, **terminal_tasks}

	def _make_depends(self, rules: Rules) -> dict[str, list[str]]:
		"""ルールを基に依存マップを生成

		Args:
			rules: ルール一覧
		Returns:
			依存マップ
		"""
		return {name: self._make_depends_of(pattern) for name, pattern in rules.items()}

	def _make_depends_of(self, pattern: PatternEntry) -> list[str]:
		"""マッチングパターンを基に依存リストを生成

		Args:
			pattern: マッチングパターンエントリー
		Returns:
			依存リスト
		"""
		if isinstance(pattern, Pattern):
			return [pattern.expression]
		else:
			return list(flatten([self._make_depends_of(in_pattern) for in_pattern in pattern]))

	@override
	def __len__(self) -> int:
		"""Returns: 要素数"""
		return len(self._tasks)

	@override
	def __iter__(self) -> KeysView[str]:
		"""Returns: イテレーター(シンボル)"""
		return self._tasks.keys()

	@override
	def keys(self) -> KeysView[str]:
		"""Returns: イテレーター(シンボル)"""
		return self._tasks.keys()

	@override
	def values(self) -> ValuesView[Task]:
		"""Returns: イテレーター(タスク)"""
		return self._tasks.values()

	@override
	def items(self) -> Iterator[tuple[str, Task]]:
		"""Returns: イテレーター(シンボル, タスク)"""
		for name, task in self._tasks.items():
			yield (name, task)

	@override
	def __getitem__(self, name: str) -> Task:
		"""Args: name: シンボル Returns: タスク"""
		return self._tasks[name]

	def lookup(self, base: str) -> list[str]:
		"""基点のシンボルから起動対象のシンボルをルックアップ

		Args:
			base: 基点のシンボル名
		Returns:
			シンボルリスト(起動対象)
		"""
		lookup_names = {base: True}
		target_names = list(lookup_names.keys())
		while len(target_names) > 0:
			name = target_names.pop(0)
			candidate_names = self[name].watches()
			add_names = {name: True for name in candidate_names if name not in lookup_names}
			lookup_names.update(add_names)
			target_names.extend(add_names.keys())

		return list(lookup_names.keys())

	def wakeup(self, names: list[str], keep_other: bool = False) -> list[str]:
		"""指定のタスクに起動イベントを発火。待機状態のシンボルを返却

		Args:
			names: シンボルリスト(起動対象)
			keep_other: True = 指定外のタスクは状態を維持, False = 指定外のタスクを休眠 (default = False)
		Returns:
			シンボルリスト(待機状態)
		"""
		if keep_other:
			return [name for name in names if self[name].wakeup(True)]
		else:
			return [name for name in self.keys() if self[name].wakeup(name in names)]

	def step(self, token: Token, by_state: States) -> list[str]:
		"""トークンの読み出しイベントを発火。状態変化したシンボルを返却

		Args:
			token: トークン
			by_state: 処理対象の状態
		Returns:
			シンボルリスト(状態変化)
		"""
		names = self.state_of(by_state)
		return [name for name in names if self[name].step(token)]

	def accept(self, by_state: States) -> list[str]:
		"""シンボル更新イベントを発火。状態変化したシンボルを返却

		Args:
			by_state: 処理対象の状態
		Returns:
			シンボルリスト(状態変化)
		"""
		state_of_a = lambda name, state: self[name].state_of(state)
		names = self.state_of(by_state)
		return [name for name in names if self[name].accept(state_of_a)]

	def state_of(self, expect: States, by_names: list[str] | None = None) -> list[str]:
		"""指定の状態のシンボルを返却

		Args:
			expect: 対象の状態
			by_names: シンボルリスト(処理対象) (default = None)
		Returns:
			シンボルリスト(対象)
		"""
		if isinstance(by_names, list):
			return [name for name in by_names if self[name].state_of(expect)]
		else:
			return [name for name in self.keys() if self[name].state_of(expect)]

	def lookup_advance(self, names: list[str], allow_names: list[str]) -> list[str]:
		"""状態が変化したシンボルから新たに起動するシンボルをルックアップ

		Args:
			names: シンボルリスト(状態変化)
			allow_names: シンボルリスト(許可対象)
		Returns:
			シンボルリスト(起動対象)
		"""
		lookup_names = {name: True for name in names}
		for name in names:
			if name not in lookup_names:
				candidate_names = self.lookup(name)
				add_names = [add_name for add_name in candidate_names if add_name not in lookup_names]
				lookup_names.update({add_name: True for add_name in add_names})

		advance_names = [name for name in lookup_names if name in allow_names]
		return self.state_of(States.Ready, by_names=advance_names)


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
		return self._parse(Tasks(self.rules), tokens, entrypoint)

	def _parse(self, tasks: Tasks, tokens: list[Token], entrypoint: str) -> Iterator[ASTEntry]:
		"""ソースコードを解析してASTを生成

		Args:
			tasks: タスク一覧
			tokens: トークンリスト
			entrypoint: 基点のシンボル名
		Returns:
			イテレーター(ASTエントリー)
		"""
		index = 0
		entries: list[ASTEntry] = []
		while index < len(tokens):
			token = tokens[index]
			tasks.wakeup(tasks.lookup(entrypoint))
			tasks.step(token, States.Idle)
			finish_names = tasks.state_of(States.Finish)
			finish_names.extend(self.accept(tasks, entrypoint))
			if len(finish_names) == 0:
				continue

			ast, entries = self.stack(token, entries, finish_names)
			yield ast

			if self.steped(finish_names):
				index += 1

	def accept(self, tasks: Tasks, entrypoint: str) -> list[str]:
		"""シンボル更新イベントを発火。完了したシンボルを返却

		Args:
			tasks: タスク一覧
			entrypoint: 基点のシンボル名
		Returns:
			シンボルリスト(処理完了)
		"""
		finish_names = []
		while True:
			update_names = tasks.accept(States.Idle)
			if len(update_names) == 0:
				break

			finish_names.extend(tasks.state_of(States.Finish, by_names=update_names))
			allow_names = tasks.lookup(entrypoint)
			lookup_names = tasks.lookup_advance(update_names, allow_names)
			tasks.wakeup(lookup_names, keep_other=True)

		return finish_names

	def steped(self, finish_names: list[str]) -> bool:
		"""トークンの読み出しが完了したか判定

		Args:
			finish_names: シンボルリスト(処理完了)
		Returns:
			True = 完了
		"""
		for name in finish_names:
			if name not in self.rules:
				return True

		return False

	def stack(self, token: Token, prev_entries: list[ASTEntry], finish_names: list[str]) -> tuple[ASTEntry, list[ASTEntry]]:
		"""今回解析した結果からASTを生成し、以前のASTを内部にスタック

		Args:
			token: トークン
			prev_entries: ASTエントリーリスト(以前)
			finish_names: シンボルリスト(処理完了)
		Returns:
			(ASTエントリー, ASTエントリーリスト(新))
		"""
		entries: list[ASTEntry] = prev_entries.copy()
		ast = entries[0] if len(entries) > 0 else ASTToken.empty()
		terminal_name = ''
		for name in finish_names:
			if name not in self.rules:
				terminal_name = name
				continue

			pattern = self.rules[name]
			if isinstance(pattern, Pattern) and pattern.role == Roles.Terminal:
				assert pattern.expression == terminal_name and pattern.expression in finish_names
				ast = ASTToken(name, token)
				entries.append(ast)
			else:
				ast = ASTTree(name, self._unwrap(entries))
				entries = [ast]

		assert isinstance(ast, ASTTree) and len(entries) == 1
		return ast, entries

	def _unwrap(self, children: list[ASTEntry]) -> list[ASTEntry]:
		"""子のASTエントリーを展開

		Args:
			children: 配下要素
		Returns:
			展開後のASTエントリーリスト
		"""
		unwraped: list[ASTEntry] = []
		for child in children:
			if isinstance(child, ASTToken):
				unwraped.append(child)
			elif self.rules.unwrap_by(child.name) == Unwraps.OneTime and len(child.children) == 1:
				unwraped.append(child.children[0])
			elif self.rules.unwrap_by(child.name) == Unwraps.Always:
				unwraped.extend(child.children)
			else:
				unwraped.append(child)

		return unwraped
