from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec('P')
T_Ret = TypeVar('T_Ret')


class Memo:
	"""キャッシュデコレーターファクトリー"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__cache: dict[str, Any] = {}

	def __call__(self, key: str) -> Callable[[Callable[P, T_Ret]], Callable[P, T_Ret]]:
		"""キャッシュデコレーターを生成

		Args:
			key (str): キャッシュキー
		Returns:
			Callable: デコレーター
		"""
		def decorator(wrapper_func: Callable[P, T_Ret]) -> Callable[P, T_Ret]:
			def wrapper(*args: P.args, **kwargs: P.kwargs) -> T_Ret:
				if key in self.__cache:
					return self.__cache[key]

				self.__cache[key] = wrapper_func(*args, **kwargs)
				return self.__cache[key]

			return wrapper

		return decorator


class Memoize:
	"""キャッシュプロバイダー"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__memos: dict[object, Memo] = {}

	def get(self, obj: object) -> Memo:
		"""オブジェクトに対応したキャッシュデコレーターファクトリーを取得

		Args:
			obj (object): オブジェクト
		Returns:
			Memo: キャッシュデコレーターファクトリー
		"""
		if obj in self.__memos:
			return self.__memos[obj]

		self.__memos[obj] = Memo()
		return self.__memos[obj]
