from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec('P')
T_Ret = TypeVar('T_Ret')


def data_provider(args_list: list[tuple], includes: list[int] = [], excludes: list[int] = []) -> Callable:
	"""テストメソッドにデータを注入するデコレーター

	Args:
		args_list: 注入する引数リスト
		includes: 注入するインデックス([]: 指定なし)
		excludes: 注入を除外するインデックス([]: 指定なし)
	Returns:
		デコレーター
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
					print(f'\n{test_func.__module__}.{self.__class__.__name__}.{test_func.__name__}: Provided No.{index}. with: {provide_args}, on error: {e.__class__.__name__}')
					raise

		return wrapper
	return decorator

