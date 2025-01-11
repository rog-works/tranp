from collections.abc import Callable
from typing import Any, ClassVar, TypeVar

from rogw.tranp.compatible.libralies.classes import __actual__

T = TypeVar('T')


class Embed:
	"""埋め込みモジュール

	Attributes:
		mutable: 変性フラグ (対象: 仮引数)
		immutable: 不変性フラグ (対象: 仮引数)
	"""

	mutable: ClassVar[bool] = True
	immutable: ClassVar[bool] = True

	@classmethod
	def python(cls, wrapped: T) -> T:
		"""Python専用としてマークアップ。Python以外の言語へのトランスパイルは対象外となる

		Args:
			wrapped: ラップ対象
		Returns:
			デコレート対象
		"""
		return wrapped

	@classmethod
	def alias(cls, name: str, prefix: bool = False) -> Callable:
		"""トランスパイル後のシンボル名を埋め込む

		Args:
			name: 名前 (default = '')
			prefix: 接頭辞フラグ (default = False)
		Returns:
			デコレート対象
		Note:
			* トランスパイル後のシンボル名のみ変更するため、シンボルテーブルには定義元の名称で登録される点に注意
			* シンボルテーブルに登録する名称を変更する場合は__actual__を使用 @see rogw.tranp.compatible.libralies.classes.__actual__
		"""
		def decorator(wrapped: T) -> T:
			return wrapped

		return decorator

	@classmethod
	def allow_override(cls, wrapped: T) -> T:
		"""関数を仮想関数としてマークアップ

		Args:
			wrapped: ラップ対象
		Returns:
			デコレート対象
		Note:
			* 純粋仮想関数は@abstractmethodを使う
			* 純粋仮想関数を除いた「仮想関数」はC++固有の概念であり、全く別物と言う扱いなので注意
		"""
		return wrapped

	@classmethod
	def pure(cls, wrapped: T) -> T:
		"""関数を副作用のない関数としてマークアップ

		Args:
			wrapped: ラップ対象
		Returns:
			デコレート対象
		Note:
			言語間の制約の差を吸収する目的で使用
		"""
		return wrapped

	@classmethod
	def private(cls, wrapped: T) -> T:
		"""関数をprivate関数としてマークアップ

		Args:
			wrapped: ラップ対象
		Returns:
			デコレート対象
		Note:
			言語間の制約の差を吸収する目的で使用
		"""
		return wrapped

	@classmethod
	def protected(cls, wrapped: T) -> T:
		"""関数をprotected関数としてマークアップ

		Args:
			wrapped: ラップ対象
		Returns:
			デコレート対象
		Note:
			言語間の制約の差を吸収する目的で使用
		"""
		return wrapped

	@classmethod
	def public(cls, wrapped: T) -> T:
		"""関数をpublic関数としてマークアップ

		Args:
			wrapped: ラップ対象
		Returns:
			デコレート対象
		Note:
			言語間の制約の差を吸収する目的で使用
		"""
		return wrapped

	@classmethod
	def struct(cls, wrapped: T) -> T:
		"""クラスを構造体としてマークアップ。暗黙的に`__struct__`と言う属性を付与する

		Args:
			wrapped: ラップ対象
		Returns:
			デコレート対象
		"""
		if not hasattr(wrapped, '__struct__'):
			setattr(wrapped, '__struct__', True)

		return wrapped

	@classmethod
	def closure_bind(cls, *symbols: Any) -> Callable:
		"""クロージャーに遅延束縛の情報を埋め込む

		Args:
			*symbols: シンボルリスト
		Returns:
			デコレーター
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
			key: キー
			meta: メタ情報
		Returns:
			デコレーター
		Examples:
			```python
			@Embed.meta('class', 'meta')
			class A: ...
			```
		"""
		def decorator(wrapped: T) -> T:
			return wrapped

		return decorator
