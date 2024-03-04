from typing import Callable, TypeVar

T = TypeVar('T')


def __actual__(name: str) -> Callable[[T], T]:
	"""コード上で実際に用いる名称を埋め込む

	Args:
		name (str): 名前
	Returns:
		Callable[[T], T]: デコレート対象
	Examples:
		```python
		@__actual__('type')
		class Type: ...
		```
	"""
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator


def __alias__() -> Callable[[T], T]:
	"""トランスパイル後に名称変更を行う対象としてタグ付けする

	Returns:
		Callable[[T], T]: デコレート対象
	Note:
		@see semantics.reflection.helper.naming.ClassDomainNaming
	Examples:
		```python
		@__alias__()
		class String: ...
		```
	"""
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator


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
