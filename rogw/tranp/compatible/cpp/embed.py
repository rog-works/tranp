from typing import Any, Callable, TypeVar

T = TypeVar('T')


def __allow_override__(wrapped: T) -> T:
	"""仮想関数としての情報を埋め込む

	Args:
		wrapped (T): ラップ対象
	Returns:
		T: デコレート対象
	Note:
		* 純粋仮想関数は@abstractmethodを使う
		* 純粋仮想関数を除いた「仮想関数」はC++固有の概念であり、全く別物と言う扱いなので注意
	Examples:
		```python
		class A:
			@__allow_override__
			def allowe_override_method(self) -> None:
				...
		```
	"""
	return wrapped


def __struct__(wrapped: T) -> T:
	"""構造体としての情報を埋め込む

	Args:
		wrapped (T): ラップ対象
	Returns:
		T: デコレート対象
	Examples:
		```python
		@__struct__
		class Struct:
			...
		```
	"""
	return wrapped


def __props__(meta: dict[str, Any]) -> Callable:
	"""プロパティの付加情報を埋め込む

	Args:
		meta (dict[str, Any]): プロパティ毎の付加情報
	Returns:
		Callable: デコレーター
	Examples:
		```python
		@__props__({'prop_a': 'A', 'prop_b': 'B'})
		class A:
			def __init__(self, a: int, b: str) -> None:
				self.prop_a: int = a
				self.prop_b: str = b
		```
	"""
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator
