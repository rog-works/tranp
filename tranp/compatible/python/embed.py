from typing import Callable, TypeVar

T = TypeVar('T')


def __actual__(name: str) -> Callable[[T], T]:
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator


def __alias__(name: str) -> Callable[[T], T]:
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator
