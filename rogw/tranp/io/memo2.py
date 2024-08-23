from typing import Callable, Generic, TypeVar

T = TypeVar('T')


class Memo(Generic[T]):
	def __init__(self, factory: Callable[[], T]) -> None:
		self._factory = factory
		self._result: T | None = None

	def get(self) -> T:
		if self._result is None:
			self._result = self._factory()

		return self._result


class Memoize:
	def __init__(self) -> None:
		self._memos: dict[object, Memo] = {}

	def get(self, key: object, factory: Callable[[], T]) -> T:
		if key not in self._memos:
			self._memos[key] = Memo(factory)

		return self._memos[key].get()
