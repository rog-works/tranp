from typing import Callable, Generic, TypeVar

T = TypeVar('T')


class Memo(Generic[T]):
	"""キャッシュ"""

	def __init__(self, factory: Callable[[], T]) -> None:
		"""インスタンスを生成

		Args:
			factory (Callable[[], T]): ファクトリー関数
		"""
		self._factory = factory
		self._result: T | None = None

	def get(self) -> T:
		if self._result is None:
			self._result = self._factory()

		return self._result


class Memoize:
	"""キャッシュマネージャー"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self._memos: dict[object, Memo] = {}

	def get(self, key: object, factory: Callable[[], T]) -> T:
		"""キャッシュからインタンスを取得

		Args:
			key (object): キャッシュキー
			factory (Callable[[], T]): ファクトリー関数
		Returns:
			T: インスタンス
		"""
		if key not in self._memos:
			self._memos[key] = Memo(factory)

		return self._memos[key].get()
