from typing import Any, Callable


class Memo:
	"""キャッシュデコレーターファクトリー"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__cache: dict[str, Any] = {}

	def __call__(self, key: str) -> Callable:
		"""キャッシュデコレーターを生成

		Args:
			key (str): キャッシュキー
		Returns:
			Callable: デコレーター
		Note:
			何万回と実行されるメソッドに対してこのキャッシュデコレーターを適用すると、
			タイプヒントによるオーバーヘッドが無視できないレベルに達する
			Callableのタイプヒントが無かったとしても実害がほぼ無いため省略することとする
		"""
		def decorator(wrapper_func: Callable) -> Callable:
			def wrapper(*args, **kwargs) -> Any:
				if key in self.__cache:
					return self.__cache[key]

				self.__cache[key] = wrapper_func(*args, **kwargs)
				return self.__cache[key]

			return wrapper

		return decorator


class Memoize:
	"""キャッシュプロバイダー

	Examples:
		```python
		# Good
		class Data:
			def __init__(self) -> None:
				self.__memo = Memoize()

			def get_very_slow(self, name: str) -> Result:
				memo = self.__memo.get(self.get_very_slow)
				@memo(name)
				def factory() -> Result:
					# some very slow process
					return result

				return factory()

		# Bad
		memo = Memoize()
		class Data:
			@memo()
			def get_very_slow(self, name: str) -> Result:
				# some very slow process
				return result
		```
	"""

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
