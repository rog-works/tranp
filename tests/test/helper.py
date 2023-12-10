from typing import Callable


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
				except Exception:
					print(f'{test_func.__module__}.{test_func.__name__}: Provided No.{index}. with: {provide_args}')
					raise

		return wrapper
	return decorator
