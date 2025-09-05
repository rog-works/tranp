import sys
import traceback

from jinja2 import Environment

from rogw.tranp.bin.io import readline


class Args:
	"""引数"""

	def __init__(self, argv: list[str]) -> None:
		"""インスタンスを生成

		Args:
			argv: 引数
		"""
		args = self.parse(argv)

	def parse(self, argv: list[str]) -> dict[str, str]:
		"""引数を解析

		Args:
			argv: 引数
		Returns:
			引数一覧
		"""
		return {}


class App:
	def __init__(self, args: Args) -> None:
		"""インスタンスを生成

		Args:
			args: 引数
		"""
		self.args = args
		self.render = Environment()

	def run(self) -> None:
		"""実行処理(インタラクティブモード)"""
		while True:
			print('==========')
			print('Jinja2 code here. Type `exit()` to quit:')

			lines: list[str] = []
			while True:
				line = readline()
				if not line:
					break

				lines.append(line)

			if len(lines) == 1 and lines[0] == 'exit()':
				break

			source = '\n'.join(lines)
			print('==========')
			print('Result')
			print('----------')
			print(self.render.from_string(source).render())


if __name__ == '__main__':
	try:
		App(Args(sys.argv[1:])).run()
	except KeyboardInterrupt:
		pass
	except Exception:
		print(traceback.format_exc())
