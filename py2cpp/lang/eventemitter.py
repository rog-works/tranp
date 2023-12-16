from typing import Callable, TypeAlias

T_Callback: TypeAlias = Callable[..., bool | None]


class EventEmitter:
	"""イベントエミッター"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__handlers: dict[str, list[T_Callback]] = {}

	def emit(self, action: str, **kwargs) -> None:
		"""イベントを発火

		Args:
			action (str): イベントタグ
			kwargs (Any): イベントデータ
		"""
		if action not in self.__handlers:
			return

		for handler in reversed(self.__handlers[action]):
			if handler(**kwargs) == False:
				break

	def on(self, action: str, callback: T_Callback) -> None:
		"""イベントハンドラーを追加

		Args:
			action (str): イベントタグ
			callback (T_Callback): イベントハンドラー
		"""
		if action not in self.__handlers:
			self.__handlers[action] = []

		if callback not in self.__handlers[action]:
			self.__handlers[action].append(callback)

	def off(self, action: str, callback: T_Callback) -> None:
		"""イベントハンドラーを解除

		Args:
			action (str): イベントタグ
			callback (T_Callback): イベントハンドラー
		"""
		if action not in self.__handlers:
			raise ValueError()

		self.__handlers[action].remove(callback)

	def clear(self) -> None:
		"""イベントハンドラーを全て解除"""
		self.__handlers = {}
