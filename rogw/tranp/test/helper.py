import functools
import os
from collections.abc import Callable

__PYTESTINDEX = int(os.environ.get('PYTESTINDEX', -1))


def data_provider(args_list: list[tuple]) -> Callable:
	"""テストメソッドにデータを注入するデコレーター

	Args:
		args_list: 注入する引数リスト
	Returns:
		デコレーター
	Note:
		環境変数にPYTESTINDEXが指定されている場合は特定のindexのみ実行 @see bin/test.sh
	"""
	def decorator(test_func: Callable):
		@functools.wraps(test_func)
		def wrapper(self, *_):
			for index, provide_args in enumerate(args_list):
				if __PYTESTINDEX != -1 and __PYTESTINDEX != index:
					continue

				try:
					test_func(self, *provide_args)
				except Exception as e:
					print(f'\n{test_func.__module__}.{self.__class__.__name__}.{test_func.__name__}: Provided No.{index}. with: {provide_args}, on error: {e.__class__.__name__}')
					raise

		return wrapper
	return decorator
