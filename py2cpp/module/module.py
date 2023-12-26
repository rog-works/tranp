from typing import TypeVar

from py2cpp.lang.locator import Locator

T = TypeVar('T')


class Module:
	def __init__(self, locator: Locator, path: str) -> None:
		self.__locator = locator
		self.__path = path

	@property
	def path(self) -> str:
		return self.__path

	def entrypoint(self, ctor: type[T]) -> T:
		# FIXME 循環参照を回避するため一旦関数内部に配置
		from py2cpp.node.node import Node

		# XXX 後のas_aによって確認されるため、冗長な判定
		if not issubclass(ctor, Node):
			raise ValueError(f'Unexpected entrypoint type. ctor: {ctor}')

		return self.__locator.resolve(Node).as_a(ctor)
