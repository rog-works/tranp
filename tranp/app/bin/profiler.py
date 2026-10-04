import os
import sys
from unittest import TestLoader, TestSuite, TextTestRunner

from tranp.app.lang.profile import profiler


class Args:
	"""引数"""

	def __init__(self, argv: list[str]) -> None:
		"""インスタンスを生成

		Args:
			argv: 引数リスト
		"""
		args = self.parse(argv)
		self.target = args['target']
		self.sort = args['sort']

	def parse(self, argv: list[str]) -> dict[str, str]:
		"""引数を解析

		Args:
			argv: 引数リスト
		Returns:
			引数リスト
		"""
		args = {
			'target': '',
			'sort': 'tottime',
		}
		while len(argv) > 0:
			arg = argv.pop(0)
			if arg == '-t':
				args['target'] = argv.pop(0)
			elif arg == '-s':
				args['sort'] = argv.pop(0)

		return args


class App:
	"""アプリケーション"""

	def __init__(self, args: Args) -> None:
		"""インスタンスを生成

		Args:
			args: 引数
		"""
		self.args = args

	def make_suite(self, target: str) -> TestSuite:
		"""Returns: テストスイート"""
		if len(target) == 0:
			test_root = os.path.join(os.getcwd(), 'tests')
			return TestLoader().discover(test_root, top_level_dir=os.getcwd())
		else:
			return TestLoader().loadTestsFromName(target)

	def run(self) -> None:
		"""実行処理"""
		suite = self.make_suite(self.args.target)
		runner = TextTestRunner()
		func = profiler(sort=self.args.sort, on=True)(runner.run)
		func(suite)


if __name__ == '__main__':
	App(Args(sys.argv[1:])).run()
