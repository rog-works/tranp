from collections.abc import Callable
from typing import Any, Protocol

from rogw.tranp.lang.annotation import duck_typed


class Observable[T_Ret](Protocol):
	"""オブザーバープロトコル"""

	def on(self, action: str, callback: Callable[..., T_Ret]) -> None:
		"""イベントハンドラーを登録

		Args:
			action: イベントタグ
			callback: イベントハンドラー
		"""
		...

	def off(self, action: str, callback: Callable[..., T_Ret]) -> None:
		"""イベントハンドラーを解除

		Args:
			action: イベントタグ
			callback: イベントハンドラー
		"""
		...


class Middleware[T_Ret]:
	"""ミドルウェア

	Note:
		```
		### ハンドラーの評価順序
		* 登録順とは逆順に評価される
		* ミドルウェアからは最後に登録したハンドラーのみ呼び出される
		* 以降はハンドラー内からnext関数をコールすることでチェーンを実現する
		### next関数
		* nextを引数に明示した場合、次のハンドラーを呼び出す関数が自動的に挿入される
		* nextを省略した場合、残りのハンドラーは無視される
		* 最初に登録したハンドラーは終端要素になるため、nextは省略するのを推奨
		```
	Examples:
		```python
		def middle(n: int, next: Callable[[], T_Ret]) -> int:
			result = next()
			return result * n

		middleware = Middleware[int]()
		middleware.on('any', lambda n: n)
		middleware.on('any', middle)
		middleware.emit('any', n=1)
		```
	"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__handlers: dict[str, list[Callable[..., T_Ret]]] = {}

	@duck_typed(Observable)
	def on(self, action: str, callback: Callable[..., T_Ret]) -> None:
		"""イベントハンドラーを登録

		Args:
			action: イベントタグ
			callback: イベントハンドラー
		"""
		if action not in self.__handlers:
			self.__handlers[action] = []

		if callback not in self.__handlers[action]:
			self.__handlers[action].insert(0, callback)

	@duck_typed(Observable)
	def off(self, action: str, callback: Callable[..., T_Ret]) -> None:
		"""イベントハンドラーを解除

		Args:
			action: イベントタグ
			callback: イベントハンドラー
		"""
		if action not in self.__handlers:
			raise ValueError()

		self.__handlers[action].remove(callback)
		if len(self.__handlers[action]) == 0:
			del self.__handlers[action]

	def usable(self, action: str) -> bool:
		"""指定のイベントにハンドラーが登録済みか判定

		Args:
			action: イベントタグ
		Returns:
			True = 登録済み
		"""
		return action in self.__handlers

	def emit(self, action: str, **event: Any) -> T_Ret:
		"""イベントを発火

		Args:
			action: イベントタグ
			**event: イベントデータ
		Returns:
			イベントの結果
		"""
		return self.__emit(action, event, 0)

	def __emit(self, action: str, event: dict[str, Any], index: int) -> T_Ret:
		"""イベントを発火

		Args:
			action: イベントタグ
			event: イベントデータ
			index: ハンドラーインデックス
		Returns:
			イベントの結果
		"""
		handler = self.__handlers[action][index]
		if 'next' in handler.__annotations__:
			return handler(**event, next=lambda: self.__emit(action, event, index + 1))
		else:
			return handler(**event)

	def clear(self) -> None:
		"""イベントハンドラーを全て解除"""
		self.__handlers = {}
