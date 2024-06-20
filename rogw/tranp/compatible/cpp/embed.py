from typing import Any, Callable, TypeVar

T = TypeVar('T')


def __allow_override__(wrapped: T) -> T:
	"""関数を仮想関数としてマークアップ

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
	"""クラスを構造体としてマークアップ

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


def __embed__(*meta: Any) -> Callable:
	"""メタ情報を埋め込む

	Args:
		*meta (Any): メタ情報
	Returns:
		Callable: デコレーター
	Examples:
		```python
		@__embed__('prop', 'a', '/** @var A */')
		@__embed__('prop', 'b', '/** @var B */')
		class A:
			def __init__(self, a: int, b: str) -> None:
				self.a: int = a
				self.b: str = b
		```
	"""
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator
