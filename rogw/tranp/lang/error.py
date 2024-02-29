import traceback
from typing import Callable, ParamSpec, TypeVar

T_Ret = TypeVar('T_Ret')
P = ParamSpec('P')


def stacktrace(error: Exception) -> list[str]:
	"""例外からスタックトレースを生成

	Args:
		error (Exception): 例外
	Returns:
		list[str]: スタックトレース
	"""
	return traceback.format_exception(type(error), error, error.__traceback__)


def raises(raise_error: type[Exception], *handle_errors: type[Exception]) -> Callable[[Callable[P, T_Ret]], Callable[P, T_Ret]]:
	"""内部で発生した例外をラップし、新たな例外で再出力するデコレーターを生成

	Args:
		raise_error (type[Exception]): 出力例外
		*handle_errors (type[Exception]): 出力例外
	Returns:
		Callable: デコレーター
	Examples:
		```python
		@raises(DomainError, ValueError, TypeError)
		def proc() -> None:
			raise ValueError('value error!')

		proc()
		> DomainError
		```
	"""
	def decorator(wrapper_func: Callable[P, T_Ret]) -> Callable[P, T_Ret]:
		def wrapper(*args: P.args, **kwargs: P.kwargs) -> T_Ret:
			try:
				return wrapper_func(*args, **kwargs)
			except handle_errors as e:
				raise raise_error(e) from e

		return wrapper

	return decorator
