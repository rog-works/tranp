from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar('T')


class Embed:
	"""埋め込みモジュール"""

	@classmethod
	def allow_override(cls, wrapped: T) -> T:
		"""関数を仮想関数としてマークアップ

		Args:
			wrapped (T): ラップ対象
		Returns:
			T: デコレート対象
		Note:
			* 純粋仮想関数は@abstractmethodを使う
			* 純粋仮想関数を除いた「仮想関数」はC++固有の概念であり、全く別物と言う扱いなので注意
		"""
		return wrapped

	@classmethod
	def pure(cls, wrapped: T) -> T:
		"""関数を副作用のない関数としてマークアップ

		Args:
			wrapped (T): ラップ対象
		Returns:
			T: デコレート対象
		Note:
			言語間の制約の差を吸収する目的で使用
		"""
		return wrapped

	@classmethod
	def private(cls, wrapped: T) -> T:
		"""関数をprivate関数としてマークアップ

		Args:
			wrapped (T): ラップ対象
		Returns:
			T: デコレート対象
		Note:
			言語間の制約の差を吸収する目的で使用
		"""
		return wrapped

	@classmethod
	def protected(cls, wrapped: T) -> T:
		"""関数をprotected関数としてマークアップ

		Args:
			wrapped (T): ラップ対象
		Returns:
			T: デコレート対象
		Note:
			言語間の制約の差を吸収する目的で使用
		"""
		return wrapped

	@classmethod
	def public(cls, wrapped: T) -> T:
		"""関数をpublic関数としてマークアップ

		Args:
			wrapped (T): ラップ対象
		Returns:
			T: デコレート対象
		Note:
			言語間の制約の差を吸収する目的で使用
		"""
		return wrapped

	@classmethod
	def struct(cls, wrapped: T) -> T:
		"""クラスを構造体としてマークアップ。暗黙的に`__struct__`と言う属性を付与する

		Args:
			wrapped (T): ラップ対象
		Returns:
			T: デコレート対象
		"""
		if not hasattr(wrapped, '__struct__'):
			setattr(wrapped, '__struct__', True)

		return wrapped

	@classmethod
	def closure_bind(cls, *symbols: Any) -> Callable:
		"""クロージャーに遅延束縛の情報を埋め込む

		Args:
			*symbols (Any): シンボルリスト
		Returns:
			Callable: デコレーター
		Examples:
			```python
			@Embed.closure_bind(self, a, b)
			def closure() -> int:
				return self.n + a + b
			```
		"""
		def decorator(wrapped: T) -> T:
			return wrapped

		return decorator

	@classmethod
	def meta(cls, key: str, meta: Any) -> Callable:
		"""メタ情報を埋め込む

		Args:
			key (str): キー
			meta (Any): メタ情報
		Returns:
			Callable: デコレーター
		Examples:
			```python
			@Embed.meta('prop.a', '/** @var A */')
			@Embed.meta('prop.b', '/** @var B */')
			class A:
				def __init__(self, a: int, b: str) -> None:
					self.a: int = a
					self.b: str = b
			```
		"""
		def decorator(wrapped: T) -> T:
			return wrapped

		return decorator
