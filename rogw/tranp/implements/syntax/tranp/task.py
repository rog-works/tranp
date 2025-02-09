from collections.abc import Iterator, Mapping, ValuesView
from typing import KeysView, override

from rogw.tranp.implements.syntax.tranp.expression import Expression, ExpressionTerminal
from rogw.tranp.implements.syntax.tranp.rule import Rules
from rogw.tranp.implements.syntax.tranp.state import Context, StateMachine, StateOf, States, Triggers
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
		states = StateMachine(States.Ready, {
			(Triggers.Wakeup, States.Ready): States.Idle,
			(Triggers.Sleep, States.Idle): States.Ready,
			(Triggers.Done, States.Idle): States.Finish,
			(Triggers.Abort, States.Idle): States.Fail,
			(Triggers.Sleep, States.Finish): States.Ready,
			(Triggers.Wakeup, States.Finish): States.Idle,
			(Triggers.Sleep, States.Fail): States.Ready,
			(Triggers.Wakeup, States.Fail): States.Idle,
		})
		states.on(Triggers.Sleep, States.Idle, lambda: self._on_reset())
		states.on(Triggers.Step, States.Idle, lambda: self._on_step())
		states.on(Triggers.Done, States.Idle, lambda: self._on_reset())
		states.on(Triggers.Abort, States.Idle, lambda: self._on_reset())
		return states

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
		return self._expression.watches(Context.new(self._cursor, self._expression_data))

	def step(self, token: Token) -> bool:
		"""トークンの読み出しイベントを発火。状態変化を返却

		Args:
			token: トークン
		Returns:
			True = 状態が変化
		"""
		trigger = self._expression.step(Context.new(self._cursor, self._expression_data), token)
		self.notify(trigger)
		return trigger != Triggers.Empty

	def accept(self, state_of: StateOf) -> bool:
		"""シンボル更新イベントを発火。状態変化を返却

		Args:
			state_of: 状態確認ハンドラー
		Returns:
			True = 状態が変化
		"""
		trigger = self._expression.accept(Context.new(self._cursor, self._expression_data), state_of)
		self.notify(trigger)
		return trigger != Triggers.Empty

	def _on_step(self) -> None:
		"""進行イベントハンドラー"""
		self._cursor += 1

	def _on_reset(self) -> None:
		"""状態リセットイベントハンドラー"""
		self._cursor = 0
		self._expression_data = Context.new_data()


class Tasks(Mapping[str, Task]):
	"""タスク一覧"""

	def __init__(self, rules: Rules) -> None:
		"""インスタンスを生成

		Args:
			rules: ルール一覧
		"""
		super().__init__()
		self._tasks = self._build_tasks(rules)

	def _build_tasks(self, rules: Rules) -> dict[str, Task]:
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
		return self.state_of(States.Ready, by_names=advance_names)
