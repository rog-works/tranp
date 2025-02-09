from collections.abc import Callable
from enum import Enum
from typing import TypeAlias


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


StateOf: TypeAlias = Callable[[str, States], bool]


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
