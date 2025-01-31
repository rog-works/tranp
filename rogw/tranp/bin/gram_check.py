import os
import sys
import traceback
from typing import TypedDict

from rogw.tranp.bin.io import readline
from rogw.tranp.implements.syntax.tranp.rules import grammar_rules, grammar_tokenizer
from rogw.tranp.implements.syntax.tranp.syntax import SyntaxParser

DictArgs = TypedDict('DictArgs', {'filepath': str})


class Args:
	"""アプリケーション引数"""

	def __init__(self, argv: list[str]) -> None:
		"""インスタンスを生成

		Args:
			argv: コマンドライン引数
		"""
		args = self.parse(argv)
		self.filepath = args['filepath']

	def parse(self, argv: list[str]) -> DictArgs:
		"""コマンドライン引数を解析

		Args:
			argv: コマンドライン引数
		Returns:
			引数一覧
		"""
		filepath = ''
		while(len(argv)):
			value = argv.pop(0)
			if value == '-i':
				filepath = argv.pop(0)

		return {'filepath': filepath}


class App:
	"""アプリケーション"""

	def __init__(self, args: Args) -> None:
		"""インスタンスを生成

		Args:
			args: 引数
		"""
		self.args = args
		self.parser = SyntaxParser(grammar_rules(), grammar_tokenizer())

	@property
	def quiet(self) -> bool:
		"""Returns: True = 実行ログなし"""
		return len(self.args.filepath) > 0

	def run(self) -> None:
		"""実行処理"""
		if len(self.args.filepath) == 0:
			self.run_interactive()
		else:
			self.run_parse()

	def run_interactive(self) -> None:
		"""実行処理(インタラクティブモード)"""
		while True:
			print('==========')
			print('Grammar code here. Type `exit()` to quit:')

			lines: list[str] = []
			while True:
				line = readline()
				if not line:
					break

				lines.append(line)

			if len(lines) == 1 and lines[0] == 'exit()':
				break

			text = '\n'.join(lines)
			tree = self.parser.parse(f'{text}\n', 'entry')
			print('==========')
			print('AST')
			print('----------')
			print(tree.pretty())

	def run_parse(self) -> None:
		"""実行処理(既存ファイルを解析)"""
		source = self.load_source(self.args.filepath)
		tree = self.parser.parse(source, 'entry')
		print(tree.pretty('\t'))

	def load_source(self, filepath: str) -> str:
		"""ソースコードを読み込み

		Args:
			args: 引数
		"""
		fullpath = os.path.abspath(os.path.join(os.getcwd(), filepath))
		with open(fullpath) as f:
			return f.read()


if __name__ == '__main__':
	app = App(Args(sys.argv[1:]))
	try:
		app.run()
	except KeyboardInterrupt:
		pass
	except Exception:
		print(traceback.format_exc())
	finally:
		if not app.quiet:
			print('Quit')
