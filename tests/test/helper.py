from typing import Callable, ParamSpec, TypeVar

P = ParamSpec('P')
T_Ret = TypeVar('T_Ret')


def data_provider(args_list: list[tuple], includes: list[int] = [], excludes: list[int] = []) -> Callable:
	"""テストメソッドにデータを注入するデコレーター

	Args:
		args_list (list[tuple]): 注入する引数リスト
		includes (list[int]): 注入するインデックス([]: 指定なし)
		excludes (list[int]): 注入を除外するインデックス([]: 指定なし)
	Returns:
		Callable: デコレーター
	"""
	def decorator(test_func: Callable):
		def wrapper(self, *_):
			for index, provide_args in enumerate(args_list):
				if len(includes) and index not in includes:
					continue

				if len(excludes) and index in excludes:
					continue

				try:
					test_func(self, *provide_args)
				except Exception as e:
					print(f'\n{test_func.__module__}.{test_func.__name__}: Provided No.{index}. with: {provide_args}, on error: {e.__class__.__name__}')
					raise

		return wrapper
	return decorator


def profiler(sort: str = 'tottime') -> Callable[[Callable[P, T_Ret]], Callable[P, T_Ret]]:
	"""プロファイルデコレーターを生成

	Args:
		sort (str): ソートカラム(tottime(消費時間)/cumtime(累積消費時間))
	Returns:
		Callable: デコレーター
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

		return wrapper

	return decorator
