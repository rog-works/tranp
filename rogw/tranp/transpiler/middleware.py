from collections.abc import Callable
from typing import Any, Protocol

from rogw.tranp.errors import Errors
from rogw.tranp.lang.annotation import duck_typed
from rogw.tranp.lang.middleware import Observable
from rogw.tranp.syntax.node.node import Node


class RenderHandler(Protocol):
	"""レンダーハンドラープロトコル"""

	def __call__(self, node: Node, template: str, vars: dict[str, Any], original: Callable[[], str]) -> str:
		"""レンダーハンドラー

		Args:
			node: ノード
			template: テンプレート名
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
		return template in self.__handlers or '*' in self.__handlers

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

	def emit(self, node: Node, template: str, vars: dict[str, Any], original: Callable[[], str]) -> str:
		"""イベントを発火

		Args:
			node: ノード
			template: テンプレート名
			vars: 変数一覧
			original: オリジナルの結果を生成するファクトリー
		Returns:
			レンダリング結果
		"""
		if '*' in self.__handlers and template in self.__handlers:
			return self.__handlers[template](node, template, vars, lambda: self.__handlers['*'](node, template, vars, original))
		elif '*' in self.__handlers:
			return self.__handlers['*'](node, template, vars, original)
		else:
			return self.__handlers[template](node, template, vars, original)
