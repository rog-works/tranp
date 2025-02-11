from collections.abc import Iterator, Mapping, ValuesView
from typing import KeysView, override

from rogw.tranp.implements.syntax.tranp.expression import Expression, ExpressionTerminal
from rogw.tranp.implements.syntax.tranp.rule import Pattern, PatternEntry, Rules
from rogw.tranp.implements.syntax.tranp.state import Context, StateMachine, StateOf, State, States, Trigger, Triggers
from rogw.tranp.implements.syntax.tranp.token import Token
from rogw.tranp.lang.sequence import flatten


class Task:
	"""タスク"""

	def __init__(self, name: str, expression: Expression) -> None:
		"""インスタンスを生成

		Args:
			name: シンボル名
			expression: 式
		"""
		self._name = name
		self._expression = expression
		self._expression_data = Context.new_data()
		self._cursor = 0
		self._states = self._build_states()

	def _build_states(self) -> StateMachine:
		"""Returns: 生成したステートマシン"""
		states = StateMachine(States.Sleep, {
			(Triggers.Lookup, States.Sleep): States.Idle,
			(Triggers.Step, States.Idle): States.Step,
			(Triggers.Done, States.Idle): States.Done,
			(Triggers.Abort, States.Idle): States.Done,
			(Triggers.Ready, States.Step): States.Idle,
			(Triggers.Ready, States.Done): States.Idle,
		})
		states.on(Triggers.Step, States.Idle, lambda: self._on_step())
		states.on(Triggers.Done, States.Idle, lambda: self._on_reset())
		states.on(Triggers.Abort, States.Idle, lambda: self._on_reset())
		return states

	def clone(self) -> 'Task':
		return Task(self.name, self._expression)

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}[{repr(self.name)}]: {self._states.state.name} #{self._cursor}>'

	@property
	def name(self) -> str:
		"""Returns: シンボル名"""
		return self._name

	def state_of(self, expect: State) -> bool:
		"""状態を確認

		Args:
			expects: 判定する状態
		Returns:
			True = 含まれる
		"""
		return self._states.state == expect

	def notify(self, trigger: Trigger) -> None:
		"""イベント通知

		Args:
			trigger: トリガー
		"""
		self._states.notify(trigger, self._build_event(trigger))

	def _build_event(self, trigger: Trigger) -> dict[State, State]:
		assert False, 'Not implemented'

	def lookup(self) -> None:
		"""起動イベントを発火"""
		self.notify(Triggers.Lookup)

	def watches(self) -> list[str]:
		"""現在の参照位置を基に参照中のシンボルリストを返却

		Returns:
			シンボルリスト
		"""
		return self._expression.watches(Context.new(self._cursor, self._expression_data))

	def step(self, token_no: int, token: Token) -> bool:
		"""トークンの読み出しイベントを発火。状態変化を返却

		Args:
			token: トークン
		Returns:
			True = 状態が変化
		"""
		trigger = self._expression.step(Context.new(self._cursor, self._expression_data), token_no, token)
		self.notify(trigger)
		return trigger != Triggers.Empty

	def accept(self, token_no: int, state_of: StateOf) -> bool:
		"""シンボル更新イベントを発火。状態変化を返却

		Args:
			state_of: 状態確認ハンドラー
		Returns:
			True = 状態が変化
		"""
		trigger = self._expression.accept(Context.new(self._cursor, self._expression_data), token_no, state_of)
		self.notify(trigger)
		return trigger != Triggers.Empty

	def _on_step(self) -> None:
		"""進行イベントハンドラー"""
		self._cursor += 1

	def _on_reset(self) -> None:
		"""状態リセットイベントハンドラー"""
		self._cursor = 0
		self._expression_data = Context.new_data()


class DependsMap:
	def __init__(self, rules: Rules) -> None:
		self.rule_in_symbols = self._build_symbols(rules)
		self.rule_of_effects = self._build_effects()
		self.rule_of_lookup = self._build_lookup()
		self.rule_of_recursive = self._build_recursive()

	def _build_symbols(self, rules: Rules) -> dict[str, list[str]]:
		return {name: self._fetch_in_symbols(pattern) for name, pattern in rules.items()}

	def _fetch_in_symbols(self, pattern: PatternEntry) -> list[str]:
		if isinstance(pattern, Pattern):
			return [pattern.expression]

		return list(flatten([self._fetch_in_symbols(in_pattern) for in_pattern in pattern]))

	def _build_effects(self) -> dict[str, list[str]]:
		rule_of_effects: dict[str, list[str]] = {}
		for name in self.rule_in_symbols.keys():
			rule_of_effects[name] = [in_name for in_name, in_symbols in self.rule_in_symbols.items() if name in in_symbols]

		return rule_of_effects

	def _build_lookup(self) -> dict[str, list[str]]:
		return {name: self._lookup(name) for name in self.names()}

	def _lookup(self, start: str) -> list[str]:
		lookup_names = {start: True}
		target_names = list(lookup_names.keys())
		while len(target_names) > 0:
			name = target_names.pop(0)
			candidate_names = self.symbols(name)
			add_names = {name: True for name in candidate_names if name not in lookup_names}
			lookup_names.update(add_names)
			target_names.extend(add_names.keys())

		return list(lookup_names.keys())

	def _build_recursive(self) -> dict[str, list[str]]:
		rule_of_recursive: dict[str, list[str]] = {}
		for name in self.names():
			rule_of_recursive[name] = [symbol for symbol in self.symbols(name) if name in self.lookup(symbol)]

		return rule_of_recursive

	def names(self) -> list[str]:
		return list(self.rule_in_symbols.keys())

	def symbols(self, name: str) -> list[str]:
		return self.rule_in_symbols[name]

	def effects(self, name: str) -> list[str]:
		return self.rule_of_effects[name]

	def lookup(self, name: str) -> list[str]:
		return self.rule_of_lookup[name]

	def recursive(self, name: str) -> bool:
		return len(self.rule_of_recursive[name]) > 0


class Tasks(Mapping[str, Task]):
	"""タスク一覧"""

	@classmethod
	def from_rules(cls, rules: Rules) -> 'Tasks':
		return cls(cls._build_tasks(rules), DependsMap(rules))

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

	def __init__(self, tasks: dict[str, Task], depends: DependsMap) -> None:
		"""インスタンスを生成

		Args:
			rules: ルール一覧
		"""
		super().__init__()
		self._tasks = tasks
		self.depends = depends

	def clone(self) -> 'Tasks':
		return Tasks({name: task.clone() for name, task in self._tasks.items()}, self.depends)

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

	def lookup(self, name: str) -> list[str]:
		"""基点のシンボルから起動対象のシンボルをルックアップ

		Args:
			name: 基点のシンボル名
		Returns:
			シンボルリスト(起動対象)
		"""
		return self.depends.lookup(name)

	def recursive_from(self, name: str) -> list[str]:
		return [effect for effect in self.depends.effects(name) if self.depends.recursive(effect)]

	def ready(self, names: list[str]) -> None:
		"""指定のタスクに起動イベントを発火

		Args:
			names: シンボルリスト(起動対象)
		"""
		for name in names:
			self[name].lookup()

	def step(self, token_no: int, token: Token) -> list[str]:
		"""トークンの読み出しイベントを発火。状態変化したシンボルを返却

		Args:
			token: トークン
		Returns:
			シンボルリスト(状態変化)
		"""
		names = self.state_of(States.Idle)
		return [name for name in names if self[name].step(token_no, token)]

	def accept(self, token_no: int) -> list[str]:
		"""シンボル更新イベントを発火。状態変化したシンボルを返却

		Args:
			by_state: 処理対象の状態
		Returns:
			シンボルリスト(状態変化)
		"""
		state_of_a = lambda name, state: self[name].state_of(state)
		names = self.state_of(States.Idle)
		return [name for name in names if self[name].accept(token_no, state_of_a)]

	def state_of(self, expect: State, names: list[str] | None = None) -> list[str]:
		"""指定の状態のシンボルを返却

		Args:
			expect: 判定する状態
			names: シンボルリスト(処理対象) (default = None)
		Returns:
			シンボルリスト(対象)
		"""
		if isinstance(names, list):
			return [name for name in names if self[name].state_of(expect)]
		else:
			return [name for name in self.keys() if self[name].state_of(expect)]

	def lookup_advance(self, names: list[str], allow_names: list[str]) -> list[str]:
		"""状態が変化したシンボルから新たに起動するシンボルをルックアップ。抽出対象は休眠状態のタスクに限定される

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
		return self.state_of(States.Sleep, names=advance_names)
