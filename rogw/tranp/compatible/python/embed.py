from typing import Callable, TypeVar

T = TypeVar('T')


def __actual__(name: str) -> Callable[[T], T]:
	"""コード上で実際に用いる名称を埋め込む

	Args:
		name (str): 名前
	Returns:
		Callable[[T], T]: デコレート対象の関数
	Examples:
		```python
		@__actual__('type')
		class Type: ...
		```
	"""
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator


def __alias__(name: str) -> Callable[[T], T]:
	"""トランスパイル後に出力される名称を埋め込む

	Args:
		name (str): 名前
	Returns:
		Callable[[T], T]: デコレート対象の関数
	Examples:
		```python
		@__alias__('std::string')
		class String: ...
		```
	"""
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator


def __hint_generic__(*template_types: TypeVar) -> Callable[[T], T]:
	"""静的解析のヒントとなる情報を埋め込む(ジェネリック用)

	Args:
		*template_types (TypeVar): テンプレートタイプのリスト
	Returns:
		Callable[[T], T]: デコレート対象の関数
	Note:
		# 利用目的
		ランタイム上でしか判断できない情報を静的解析出来るようにするため、クラス・ファンクションに補足情報を埋め込む
	Examples:
		```python
		T = TypeVar('T')

		class GenericBase(Generic[T]): ...

		@__hint_generic__(T)
		class GenericSub(GenericBase[T]): ...
		```
	"""
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator
