from typing import Generic, TypeVar

T = TypeVar('T')


class Callable: ...
class Sequence: ...


class Iterator(Generic[T]):
	def __next__(self) -> T: ...
