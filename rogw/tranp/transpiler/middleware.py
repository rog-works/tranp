from collections.abc import Callable
from typing import Any, Protocol

from rogw.tranp.errors import Errors
from rogw.tranp.lang.annotation import duck_typed
from rogw.tranp.lang.middleware import Observable
from rogw.tranp.syntax.node.node import Node


class RenderHandler(Protocol):
	"""レンダーハンドラープロトコル"""

	def __call__(self, node: Node, vars: dict[str, Any], original: Callable[[], str]) -> str:
		"""レンダーハンドラー

		Args:
			node: ノード
			vars: 変数一覧
			original: オリジナルの結果を生成するファクトリー
		Returns:
			レンダリング結果
		"""
		...


class RenderMiddleware:
	"""レンダーミドルウェア"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__handlers: dict[str, RenderHandler] = {}

	def usable(self, template: str) -> bool:
		"""ハンドラーが登録済みか判定

		Args:
			template: テンプレート名
		Returns:
			True = 登録済み
		"""
		return template in self.__handlers

	@duck_typed(Observable.on)
	def on(self, template: str, handler: RenderHandler) -> None:
		"""ハンドラーを登録

		Args:
			template: テンプレート名
			callback: ハンドラー
		Raises:
			Errors.Logic: ハンドラーが登録済み
		"""
		if template in self.__handlers:
			raise Errors.Logic(f'Middleware already defined. "{template}"')

		self.__handlers[template] = handler

	def emit(self, template: str, node: Node, vars: dict[str, Any], original: Callable[[], str]) -> str:
		"""イベントを発火

		Args:
			template: テンプレート名
			node: ノード
			vars: 変数一覧
			original: オリジナルの結果を生成するファクトリー
		Returns:
			レンダリング結果
		"""
		return self.__handlers[template](node, vars, original)
