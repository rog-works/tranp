from typing import Generic, TypeVar

T = TypeVar('T')

class A(Generic[T]):
	value: T

	def __init__(self, value: T) -> None:
		self.value = value


a = A(0)
