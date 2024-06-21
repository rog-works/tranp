from typing import Callable, TypeVar

from rogw.tranp.compatible.libralies.classes import __actual__

T = TypeVar('T')


def __hint_generic__(*template_types: TypeVar) -> Callable[[T], T]:
	"""静的解析のヒントとなる情報を埋め込む(ジェネリッククラス用)

	Args:
		*template_types (TypeVar): テンプレートタイプのリスト
	Returns:
		Callable[[T], T]: デコレート対象
	Note:
		継承した親クラスがジェネリッククラスか否かはシンタックスから判断できないため、
		派生クラスに継承したテンプレートタイプを埋め込み、静的に解決出来るようにする
	Examples:
		```python
		T = TypeVar('T')

		class GenericBase(Generic[T]): ...

		class GenericUnknown(GenericBase[T]): ...

		@__hint_generic__(T)
		class GenericKnownT(GenericBase[T]): ...
		```
	"""
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator
