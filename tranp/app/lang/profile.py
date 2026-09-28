from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec('P')
T_Ret = TypeVar('T_Ret')


def profiler(sort: str = 'tottime', on: bool = True) -> Callable[[Callable[P, T_Ret]], Callable[P, T_Ret]]:
	"""プロファイルデコレーターを生成

	Args:
		sort: ソートカラム(tottime(消費時間)/cumtime(累積消費時間))
		on: True = 有効
	Returns:
		デコレーター
	Note:
		プロファイル結果は標準出力に出力
	Example:
		```python
		@profiler()
		def slow_function() -> None:
			...
		```
	"""
	def decorator(wrapper_func: Callable[P, T_Ret]) -> Callable[P, T_Ret]:
		def wrapper(*args: P.args, **kwargs: P.kwargs) -> T_Ret:
			import cProfile
			pr = cProfile.Profile()
			pr.enable()
			result = wrapper_func(*args, **kwargs)
			pr.disable()
			pr.print_stats(sort=sort)
			return result

		return wrapper if on else wrapper_func

	return decorator
