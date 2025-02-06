from collections.abc import Callable
import os
import sys
import traceback
from typing import TypeAlias, TypedDict

from lark import Lark
from lark.indenter import PythonIndenter

from rogw.tranp.bin.io import readline
from rogw.tranp.implements.syntax.tranp.rules import python_rules
from rogw.tranp.implements.syntax.tranp.syntax import SyntaxParser

DictArgs = TypedDict('DictArgs', {'filepath': str, 'parser': str, 'grammar': str})
Parser: TypeAlias = Callable[[str], str]

class Args:
	"""アプリケーション引数"""

	def __init__(self, argv: list[str]) -> None:
		"""インスタンスを生成

		Args:
			argv: コマンドライン引数
		"""
		args = self.parse(argv)
		self.filepath = args['filepath']
		self.parser = args['parser']
		self.grammar = args['grammar']

	def parse(self, argv: list[str]) -> DictArgs:
		"""コマンドライン引数を解析

		Args:
			argv: コマンドライン引数
		Returns:
			引数一覧
		"""
		filepath = ''
		parser = 'lark'
		grammar = 'data/grammar.lark'
		while len(argv) != 0:
			arg = argv.pop(0)
			if arg == '-i':
				filepath = argv.pop(0)
			elif arg == '-p':
				parser = argv.pop(0)
			elif arg == '-g':
				grammar = argv.pop(0)

		return {
			'filepath': filepath,
			'parser': parser,
			'grammar': grammar,
		}


class App:
	"""アプリケーション"""

	def __init__(self, args: Args) -> None:
		"""インスタンスを生成

		Args:
			args: 引数
		"""
		self.args = args

	@property
	def quiet(self) -> bool:
		"""Returns: True = 実行ログなし"""
		return len(self.args.filepath) > 0

	def run(self) -> None:
		"""実行処理"""
		parser = self.make_parser(self.args.parser)
		if len(self.args.filepath) == 0:
			self.run_interactive(parser)
		else:
			self.run_parse(parser)

	def run_interactive(self, parser: Parser) -> None:
		"""実行処理(インタラクティブモード)

		Args:
			parser: パーサー
		"""
		while True:
			print('==========')
			print('Python code here. Type `exit()` to quit:')

			lines: list[str] = []
			while True:
				line = readline()
				if not line:
					break

				lines.append(line)

			if len(lines) == 1 and lines[0] == 'exit()':
				break

			text = '\n'.join(lines)
			ast = parser(f'{text}\n')
			print('==========')
			print('AST')
			print('----------')
			print(ast)

	def run_parse(self, parser: Parser) -> None:
		"""実行処理(既存ファイルを解析)

		Args:
			parser: パーサー
		"""
		source = self.load_file(self.args.filepath)
		print(parser(source))

	def load_file(self, filepath: str) -> str:
		"""ファイルを読み込み

		Args:
			args: 引数
		Returns:
			テキスト
		"""
		fullpath = os.path.abspath(os.path.join(os.getcwd(), filepath))
		with open(fullpath, mode='rb') as f:
			return f.read().decode('utf-8')

	def make_parser(self, name: str) -> Parser:
		"""パーサーを生成

		Args:
			name: パーサーの名前
		Returns:
			パーサー
		"""
		if name == 'lark':
			grammar = self.load_file(self.args.grammar)
			parser = Lark(grammar, start='file_input', postlex=PythonIndenter(), parser='lalr')
			return lambda source: parser.parse(source).pretty()
		else:
			parser = SyntaxParser(python_rules())
			return lambda source: parser.parse(source, 'entry').pretty()


if __name__ == '__main__':
	args = Args(sys.argv[1:])
	app = App(args)
	try:
		app.run()
	except KeyboardInterrupt:
		pass
	except Exception:
		print(traceback.format_exc())
	finally:
		if not app.quiet:
			print('Quit')
