import traceback
from typing import Any, Callable, ParamSpec

P = ParamSpec('P')


def stacktrace(error: Exception) -> list[str]:
	return traceback.format_exception(type(error), error, error.__traceback__)


def raises(raise_error: type[Exception], *handle_errors: type[Exception]) -> Callable[[Callable[P, Any]], Callable[P, Any]]:
	def decorator(wrapper_func: Callable[P, Any]) -> Callable[P, Any]:
		def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
			try:
				return wrapper_func(*args, **kwargs)
			except handle_errors as e:
				raise raise_error(e) from e

		return wrapper

	return decorator
