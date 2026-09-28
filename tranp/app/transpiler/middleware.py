from typing import Any, Protocol

from tranp.app.errors import Errors
from tranp.app.lang.annotation import duck_typed
from tranp.app.lang.middleware import Observable
from tranp.app.syntax.node.node import Node
from tranp.app.view.render import Renderer


class RenderHandler(Protocol):
	"""レンダーハンドラープロトコル"""

	def __call__(self, view: Renderer, node: Node, action: str, vars: dict[str, Any]) -> str:
		"""レンダーハンドラー

		Args:
			view: ソースレンダー
			node: ノード
			action: アクション名(=テンプレート名)
			vars: 変数一覧
		Returns:
			レンダリング結果
		"""
		...


class RenderMiddleware:
	"""レンダーミドルウェア"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__handlers: dict[str, RenderHandler] = {}

	def usable(self, action: str) -> bool:
		"""ハンドラーが登録済みか判定

		Args:
			action: アクション名(=テンプレート名)
		Returns:
			True = 登録済み
		"""
		return action in self.__handlers or '*' in self.__handlers

	@duck_typed(Observable.on)
	def on(self, action: str, callback: RenderHandler) -> None:
		"""ハンドラーを登録

		Args:
			action: アクション名(=テンプレート名)
			callback: ハンドラー
		Raises:
			Errors.Logic: ハンドラーが登録済み
		"""
		if action in self.__handlers:
			raise Errors.Logic(f'Middleware already exists. "{action}"')

		self.__handlers[action] = callback

	def emit(self, view: Renderer, node: Node, action: str, vars: dict[str, Any]) -> str:
		"""イベントを発火

		Args:
			view: ソースレンダー
			node: ノード
			action: アクション名(=テンプレート名)
			vars: 変数一覧
		Returns:
			レンダリング結果
		"""
		if action in self.__handlers:
			return self.__handlers[action](view, node, action, vars)
		else:
			return self.__handlers['*'](view, node, action, vars)
