from typing import Callable, TypeVar

T = TypeVar('T')


def alias(name: str) -> Callable[[T], T]:
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator
