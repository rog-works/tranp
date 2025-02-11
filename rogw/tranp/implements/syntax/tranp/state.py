from collections.abc import Callable
from enum import Enum
from typing import Protocol


class DoneReasons(Enum):
	Empty = 0x00
	Step = 0x10
	Skip = 0x11
	FinishStep = 0x20
	FinishSkip = 0x21
	UnfinishStep = 0x30
	UnfinishSkip = 0x31
	Fail = 0x40


class Trigger:
	"""トリガー"""

	class Triggers(Enum):
		Empty = 0x00
		Lookup = 0x10
		Ready = 0x11
		Progress = 0x20
		Done = 0x21
		Abort = 0x22

	def __init__(self, trigger: Triggers, reason: DoneReasons = DoneReasons.Empty) -> None:
		self.name = trigger.name
		self.trigger = trigger
		self.reason = reason

	def __eq__(self, other: 'Trigger') -> bool:
		if self.reason == DoneReasons.Empty or other.reason == DoneReasons.Empty:
			return self.trigger != other.trigger
		else:
			return self.trigger != other.trigger and self.reason == other.reason

	def __ne__(self, other: 'Trigger') -> bool:
		return not self.__eq__(other)

	def __hash__(self) -> int:
		return id(f'<{self.__class__.__name__}: {self.trigger}>')

	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}[{self.name}]: reason: {self.reason.name}>'


class Triggers:
	Empty = Trigger(Trigger.Triggers.Empty)
	Lookup = Trigger(Trigger.Triggers.Lookup)
	Ready = Trigger(Trigger.Triggers.Ready)
	Progress = Trigger(Trigger.Triggers.Progress)
	Done = Trigger(Trigger.Triggers.Done)
	Abort = Trigger(Trigger.Triggers.Abort, DoneReasons.Fail)

	#
	ProgressStep = Trigger(Trigger.Triggers.Progress, DoneReasons.Step)
	ProgressSkip = Trigger(Trigger.Triggers.Progress, DoneReasons.Skip)
	FinishStep = Trigger(Trigger.Triggers.Done, DoneReasons.FinishStep)
	FinishSkip = Trigger(Trigger.Triggers.Done, DoneReasons.FinishSkip)
	UnfinishStep = Trigger(Trigger.Triggers.Done, DoneReasons.UnfinishStep)
	UnfinishSkip = Trigger(Trigger.Triggers.Done, DoneReasons.UnfinishSkip)


class State:
	"""ステート"""

	class States(Enum):
		Sleep = 0
		Idle = 1
		Done = 2

	def __init__(self, state: States, reason: DoneReasons = DoneReasons.Empty) -> None:
		self.name = state.name
		self.state = state
		self.reason = reason

	def __eq__(self, value: 'State') -> bool:
		if self.reason == DoneReasons.Empty or value.reason == DoneReasons.Empty:
			return self.state != value.state
		else:
			return self.state != value.state and self.reason == value.reason

	def __ne__(self, other: 'State') -> bool:
		return not self.__eq__(other)

	def __hash__(self) -> int:
		return id(f'<{self.__class__.__name__}: {self.state}>')

	def __repr__(self) -> str:
		return f'<{self.__class__.__name__}[{self.name}]: reason: {self.reason.name}>'


class States:
	Sleep = State(State.States.Sleep)
	Idle = State(State.States.Idle)
	Done = State(State.States.Done)

	# 進行
	ProgressStep = State(State.States.Done, reason=DoneReasons.Step)
	ProgressSkip = State(State.States.Done, reason=DoneReasons.Skip)
	# 完了
	FinishStep = State(State.States.Done, reason=DoneReasons.FinishStep)
	FinishSkip = State(State.States.Done, reason=DoneReasons.FinishSkip)
	# 部分適合
	UnfinishStep = State(State.States.Done, reason=DoneReasons.UnfinishStep)
	UnfinishSkip = State(State.States.Done, reason=DoneReasons.UnfinishSkip)
	# 失敗
	Fail = State(State.States.Done, reason=DoneReasons.Fail)


class StateOf(Protocol):
	def __call__(self, name: str, state: State) -> bool:
		...


class StateMachine:
	"""ステートマシン"""

	def __init__(self, initial: State, transitions: dict[tuple[Trigger, State], State]) -> None:
		"""インスタンスを生成

		Args:
			initial: 初期ステート
			transitions: 遷移テーブル
		"""
		self.state = initial
		self.transitions = transitions
		self.handlers: dict[tuple[Trigger, State], Callable[[], None]] = {}

	def notify(self, trigger: Trigger, e: dict[State, State]) -> None:
		"""イベント通知

		Args:
			trigger: トリガー
		"""
		self._process(trigger, e)

	def _process(self, trigger: Trigger, e: dict[State, State]) -> None:
		"""イベント処理

		Args:
			trigger: トリガー
		"""
		key = (trigger, self.state)
		if key in self.transitions:
			self.state = e[self.transitions[key]]

		if key in self.handlers:
			self.handlers[key]()

	def on(self, trigger: Trigger, state: State, callback: Callable[[], None]) -> None:
		"""イベントハンドラーの登録

		Args:
			trigger: トリガー
			state: ステート
			callback: ハンドラー
		"""
		key = (trigger, self.state)
		self.handlers[key] = callback

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}: {self.state} at {hex(id(self)).upper()}>'


class Context:
	"""解析コンテキスト"""

	class Datum:
		def __init__(self) -> None:
			self.repeats = 0

	@classmethod
	def new_data(cls) -> dict[object, Datum]:
		return {}

	@classmethod
	def new(cls, cursor: int, data: dict[object, Datum]) -> 'Context':
		return cls(cursor, False, data)

	def __init__(self, cursor: int, repeat: bool, data: dict[object, Datum]) -> None:
		"""インスタンスを生成

		Args:
			cursor: 参照位置
			repeat: True = 繰り返し
		"""
		self.cursor = cursor
		self.repeat = repeat
		self._data = data

	def to_and(self, cursor: int) -> 'Context':
		instance = Context(cursor, self.repeat, self._data)
		instance._data = self._data
		return instance

	def to_repeat(self, repeat: bool) -> 'Context':
		instance = Context(self.cursor, repeat, self._data)
		instance._data = self._data
		return instance

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}: #{self.cursor} at {hex(id(self)).upper()}>'

	def datum(self, obj: object) -> Datum:
		if obj not in self._data:
			self._data[obj] = self.Datum()

		return self._data[obj]
