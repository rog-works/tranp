from typing import Any, Callable, Generic, Protocol, TypeAlias, TypeVar

from rogw.tranp.lang.annotation import duck_typed

T_Ret = TypeVar('T_Ret')

Callback: TypeAlias = Callable[..., T_Ret | None]


class IObservable(Protocol):
	"""オブザーバープロトコル"""

	def on(self, action: str, callback: Callback) -> None:
		"""イベントハンドラーを登録

		Args:
			action (str): イベントタグ
			callback (Callback): イベントハンドラー
		"""
		...

	def off(self, action: str, callback: Callback) -> None:
		"""イベントハンドラーを解除

		Args:
			action (str): イベントタグ
			callback (Callback): イベントハンドラー
		"""
		...


class EventEmitter(Generic[T_Ret]):
	"""イベントエミッター"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__handlers: dict[str, list[Callback[T_Ret]]] = {}

	@duck_typed(IObservable)
	def on(self, action: str, callback: Callback[T_Ret]) -> None:
		"""イベントハンドラーを登録

		Args:
			action (str): イベントタグ
			callback (Callback[T_Ret]): イベントハンドラー
		"""
		if action not in self.__handlers:
			self.__handlers[action] = []

		if callback not in self.__handlers[action]:
			self.__handlers[action].append(callback)

	@duck_typed(IObservable)
	def off(self, action: str, callback: Callback[T_Ret]) -> None:
		"""イベントハンドラーを解除

		Args:
			action (str): イベントタグ
			callback (Callback[T_Ret]): イベントハンドラー
		"""
		if action not in self.__handlers:
			raise ValueError()

		self.__handlers[action].remove(callback)

	def observed(self, action: str) -> bool:
		"""指定のイベントにハンドラーが登録済みか判定

		Args:
			action (str): イベントタグ
		Returns:
			bool: True = 登録済み
		"""
		return action in self.__handlers

	def emit(self, action: str, **event: Any) -> T_Ret | None:
		"""イベントを発火

		Args:
			action (str): イベントタグ
			event (Any): イベントデータ
		Returns:
			T_Ret | None: イベントの結果
		Note:
			XXX null以外の結果が取得出来た場合は以降のハンドラーを省略する
		"""
		if action not in self.__handlers:
			return None

		for handler in reversed(self.__handlers[action]):
			result = handler(**event)
			if result is not None:
				return result

		return None

	def clear(self) -> None:
		"""イベントハンドラーを全て解除"""
		self.__handlers = {}
