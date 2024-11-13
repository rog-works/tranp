from collections.abc import Callable
import traceback
from types import TracebackType
from typing import ParamSpec, TypeVar

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
		*handle_errors (type[Exception]): ハンドリング対象の例外
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


class Transaction:
	"""トランザクションエラーハンドラー"""

	def __init__(self, raise_error: type[Exception], *handle_errors: type[Exception]) -> None:
		"""インスタンスを生成

		Args:
			raise_error (type[Exception]): 出力例外
			*handle_errors (type[Exception]): ハンドリング対象の例外
		"""
		self._raise_error = raise_error
		self._handle_errors = handle_errors

	def __enter__(self) -> 'Transaction':
		"""ハンドラー(ブロック開始)"""
		return self

	def __exit__(self, exc_type: type[Exception], exc_value: BaseException | None, exc_traceback: TracebackType):
		"""ハンドラー(ブロック終了)

		Args:
			exc_type (type[Exception]): 出力例外の型
			exc_value (BaseException | None): 出力例外
			exc_traceback (TracebackType): トレースバック
		"""
		if exc_value and issubclass(exc_type, self._handle_errors):
			raise self._raise_error(exc_value) from exc_value
