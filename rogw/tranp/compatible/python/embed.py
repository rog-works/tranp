from typing import Any, Callable, TypeVar

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


def __hint__(data: dict[str, Any]) -> Callable[[T], T]:
	"""静的解析のヒントとなる情報を埋め込む

	Args:
		data (dict[str, Any]): 補足情報 XXX **kwargsを実装
	Returns:
		Callable[[T], T]: デコレート対象の関数
	Note:
		# 利用目的
		ランタイム上でしか判断できない情報を静的に解決出来るようにするため、クラス・ファンクションに補足情報を埋め込む
		# dataの書式
		`@__hint__({'$node.prop_name': Any, ...})`
	Examples:
		```python
		T = TypeVar('T')

		class GenericBase(Generic[T]): ...

		@__hint__({'generic_types': T})
		class GenericSub(GenericBase[T]): ...
		```
	"""
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator
