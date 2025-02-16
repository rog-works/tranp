from collections.abc import Iterator, Mapping, ValuesView
from typing import KeysView, override

from rogw.tranp.implements.syntax.tranp.expression import Expression, ExpressionTerminal
from rogw.tranp.implements.syntax.tranp.rule import RuleMap, Rules
from rogw.tranp.implements.syntax.tranp.state import Context, DoneReasons, StateMachine, StateOf, States, Triggers
from rogw.tranp.implements.syntax.tranp.token import Token
from rogw.tranp.lang.sequence import flatten


class Task:
	"""タスク"""

	def __init__(self, name: str, expression: Expression, states: StateMachine | None = None) -> None:
		"""インスタンスを生成

		Args:
			name: シンボル名
			expression: 式
		"""
		self._name = name
		self._expression = expression
		self._expression_store = Context.new_store()
		self._cursor = 0
		self._states = states if states else self._build_states()
		self._reason = DoneReasons.Empty
		self._bind_states(self._states)

	def _build_states(self) -> StateMachine:
		"""Returns: 生成したステートマシン"""
		return StateMachine(States.Sleep, {
			(Triggers.Ready, States.Sleep): States.Idle,
			(Triggers.Step, States.Idle): States.Step,
			(Triggers.Done, States.Idle): States.Done,
			(Triggers.Abort, States.Idle): States.Abort,
			(Triggers.Ready, States.Step): States.Idle,
			(Triggers.Ready, States.Done): States.Idle,
			(Triggers.Ready, States.Abort): States.Idle,
		})

	def _bind_states(self, states: StateMachine) -> None:
		states.on(Triggers.Skip, States.Idle, lambda: self._on_step())
		states.on(Triggers.Step, States.Idle, lambda: self._on_step())
		states.on(Triggers.Done, States.Idle, lambda: self._on_reset())
		states.on(Triggers.Abort, States.Idle, lambda: self._on_reset())

	def clone(self) -> 'Task':
		return Task(self.name, self._expression, self._states.clone())

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}[{repr(self.name)}]: {self._states.state} #{self._cursor}>'

	@property
	def name(self) -> str:
		"""Returns: シンボル名"""
		return self._name

	def state_of(self, expect: States, reason: DoneReasons) -> bool:
		"""状態を確認

		Args:
			expects: 判定する状態
		Returns:
			True = 含まれる
		"""
		if reason == DoneReasons.Empty:
			return self._states.state == expect
		else:
			return self._states.state == expect and (self._reason.value & reason.value) == reason.value

	def notify(self, trigger: Triggers, reason: DoneReasons) -> None:
		"""イベント通知

		Args:
			trigger: トリガー
		"""
		before = self._states.state
		self._states.notify(trigger)
		if before != self._states:
			self._reason = reason

	def watches(self) -> list[str]:
		"""現在の参照位置を基に参照中のシンボルリストを返却

		Returns:
			シンボルリスト
		"""
		return self._expression.watches(Context.make(self._cursor, self._expression_store))

	def ready(self) -> None:
		"""起動イベントを発火"""
		self.notify(Triggers.Ready, DoneReasons.Empty)

	def step(self, token_no: int, token: Token) -> bool:
		"""トークンの読み出しイベントを発火。状態変化イベントの有無を返却

		Args:
			token_no: トークンNo
			token: トークン
		Returns:
			True = 状態変化イベントが発生
		"""
		trigger, reason = self._expression.step(Context.make(self._cursor, self._expression_store), token_no, token)
		self.notify(trigger, reason)
		return trigger != Triggers.Empty

	def accept(self, token_no: int, state_of: StateOf) -> bool:
		"""シンボル更新イベントを発火。状態変化イベントの有無を返却

		Args:
			token_no: トークンNo
			state_of: 状態確認ハンドラー
		Returns:
			True = 状態変化イベントが発生
		"""
		trigger, reason = self._expression.accept(Context.make(self._cursor, self._expression_store), token_no, state_of)
		self.notify(trigger, reason)
		return trigger != Triggers.Empty

	def _on_step(self) -> None:
		"""進行イベントハンドラー"""
		self._cursor += 1

	def _on_reset(self) -> None:
		"""状態リセットイベントハンドラー"""
		self._cursor = 0
		self._expression_store = Context.new_store()


class Tasks(Mapping[str, Task]):
	"""タスク一覧"""

	@classmethod
	def from_rules(cls, rules: Rules) -> 'Tasks':
		return cls(cls._build_tasks(rules), RuleMap(rules))

	@classmethod
	def _build_tasks(cls, rules: Rules) -> dict[str, Task]:
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

	def __init__(self, tasks: dict[str, Task], _rule_map: RuleMap) -> None:
		"""インスタンスを生成

		Args:
			rules: ルール一覧
		"""
		super().__init__()
		self._tasks = tasks
		self._rule_map = _rule_map

	def clone(self) -> 'Tasks':
		return Tasks({name: task.clone() for name, task in self._tasks.items()}, self._rule_map)

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

	def state_of(self, expect: States, names: list[str] | None = None) -> list[str]:
		"""指定の状態のシンボルを返却

		Args:
			expect: 判定する状態
			names: シンボルリスト(処理対象) (default = None)
		Returns:
			シンボルリスト(対象)
		"""
		by_names = names if isinstance(names, list) else list(self.keys())
		return [name for name in by_names if self[name].state_of(expect, DoneReasons.Empty)]

	def lookup(self, base: str) -> list[str]:
		"""基点のシンボルから起動対象のシンボルをルックアップ

		Args:
			base: 基点のシンボル名
		Returns:
			シンボルリスト(起動対象)
		"""
		return self._rule_map.lookup(base)

	def recursive_from(self, base: str, names: list[str]) -> list[tuple[str, str]]:
		priorities = self.lookup(base)
		pair_names: list[tuple[str, str]] = []
		for via_name in names:
			for name in self._rule_map.effects(via_name):
				recursive = self._rule_map.recursive(name)
				if len(recursive) == 0:
					continue

				if priorities.index(name) < priorities.index(via_name):
					continue

				pair_names.append((via_name, name))

		return pair_names

	def ready(self, names: list[str]) -> None:
		"""指定のタスクに起動イベントを発火

		Args:
			names: シンボルリスト(起動対象)
		"""
		for name in names:
			self[name].ready()

	def step(self, token_no: int, token: Token) -> list[str]:
		"""トークンの読み出しイベントを発火。状態変化イベントが発生したシンボルを返却

		Args:
			token_no: トークンNo
			token: トークン
		Returns:
			シンボルリスト(状態変化)
		"""
		names = self.state_of(States.Idle)
		return [name for name in names if self[name].step(token_no, token)]

	def accept(self, token_no: int) -> list[str]:
		"""シンボル更新イベントを発火。状態変化イベントが発生したシンボルを返却

		Args:
			token_no: トークンNo
		Returns:
			シンボルリスト(状態変化)
		"""
		state_of_a = lambda name, state, reason: self[name].state_of(state, reason)
		names = self.state_of(States.Idle)
		return [name for name in names if self[name].accept(token_no, state_of_a)]
