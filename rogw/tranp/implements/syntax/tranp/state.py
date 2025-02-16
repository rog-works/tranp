from collections.abc import Callable
from enum import Enum
from typing import Protocol


class DoneReasons(Enum):
	Empty = 0x00
	Skip = 0x01
	Step = 0x02
	Match = 0x04
	Finish = 0x08

	MatchSkip = 0x04 | 0x01
	MatchStep = 0x04 | 0x02
	FinishSkip = 0x08 | 0x04 | 0x01
	FinishStep = 0x08 | 0x04 | 0x02

	@property
	def physically(self) -> bool:
		return (self.value & DoneReasons.Step.value) != 0

	@property
	def match(self) -> bool:
		return (self.value & DoneReasons.Match.value) != 0

	@property
	def finish(self) -> bool:
		return (self.value & DoneReasons.Finish.value) != 0

	@property
	def unfinish(self) -> bool:
		return self.match and not self.finish


class Triggers(Enum):
	Empty = 0
	Ready = 1
	Skip = 2
	Step = 3
	Done = 4
	Abort = 5


class States(Enum):
	Sleep = 0
	Idle = 1
	Step = 2
	Done = 3
	Abort = 4


class StateOf(Protocol):
	def __call__(self, name: str, state: States, reason: DoneReasons) -> bool:
		...


class StateMachine:
	"""ステートマシン"""

	def __init__(self, initial: States, transitions: dict[tuple[Triggers, States], States]) -> None:
		"""インスタンスを生成

		Args:
			initial: 初期ステート
			transitions: 遷移テーブル
		"""
		self.initial = initial
		self.state = initial
		self.transitions = transitions
		self.handlers: dict[tuple[Triggers, States], Callable[[], None]] = {}

	def clone(self) -> 'StateMachine':
		return StateMachine(self.initial, self.transitions)

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
		return f'<{self.__class__.__name__}: {self.state} at {hex(id(self)).upper()}>'


class StateStore:
	def __init__(self, trigger: Triggers = Triggers.Empty, reason: DoneReasons = DoneReasons.Empty, order: int = -1, token_no: int = -1) -> None:
		self.trigger = trigger
		self.reason = reason
		self.order = order
		self.token_no = token_no


class Context:
	"""解析コンテキスト"""

	class StoreEntry:
		def __init__(self) -> None:
			self.state_stores: list[StateStore] = []

	@classmethod
	def new_store(cls) -> dict[object, StoreEntry]:
		return {}

	@classmethod
	def make(cls, cursor: int, store: dict[object, StoreEntry]) -> 'Context':
		return cls(cursor, False, store)

	def __init__(self, cursor: int, repeat: bool, store: dict[object, StoreEntry]) -> None:
		"""インスタンスを生成

		Args:
			cursor: 参照位置
			repeat: True = 繰り返し
		"""
		self.cursor = cursor
		self.repeat = repeat
		self._store = store

	def to_and(self, cursor: int) -> 'Context':
		instance = Context(cursor, self.repeat, self._store)
		instance._store = self._store
		return instance

	def to_repeat(self, repeat: bool) -> 'Context':
		instance = Context(self.cursor, repeat, self._store)
		instance._store = self._store
		return instance

	def __repr__(self) -> str:
		"""Returns: シリアライズ表現"""
		return f'<{self.__class__.__name__}: #{self.cursor} at {hex(id(self)).upper()}>'

	def store_by(self, owner: object) -> StoreEntry:
		if owner not in self._store:
			self._store[owner] = self.StoreEntry()

		return self._store[owner]
