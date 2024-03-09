from typing import TypeVar

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
