from collections.abc import Callable
import os
import sys
from typing import TypeAlias, TypedDict

from lark import Lark
from lark.indenter import PythonIndenter

from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.bin.io import tty
from rogw.tranp.implements.syntax.tranp.rule import Rules
from rogw.tranp.implements.syntax.tranp.rules import grammar_rules, grammar_tokenizer
from rogw.tranp.implements.syntax.tranp.syntax import SyntaxParser
from rogw.tranp.lang.error import stacktrace

DictArgs = TypedDict('DictArgs', {'input': str, 'parser': str, 'grammar': str, 'help': bool})
Parser: TypeAlias = Callable[[str], str]


class Args:
	"""アプリケーション引数"""

	def __init__(self, argv: list[str]) -> None:
		"""インスタンスを生成

		Args:
			argv: コマンドライン引数
		"""
		args = self.parse(argv)
		self.input = args['input']
		self.parser = args['parser']
		self.grammar = args['grammar']
		self.help = args['help']

	def parse(self, argv: list[str]) -> DictArgs:
		"""コマンドライン引数を解析

		Args:
			argv: コマンドライン引数
		Returns:
			引数一覧
		"""
		args: DictArgs = {
			'input': '',
			'parser': 'lark',
			'grammar': os.path.join(tranp_dir(), 'data/grammar.lark'),
			'help': False,
		}
		while len(argv) != 0:
			arg = argv.pop(0)
			if arg == '-i':
				args['input'] = argv.pop(0)
			elif arg == '-p':
				args['parser'] = argv.pop(0)
			elif arg == '-g':
				args['grammar'] = argv.pop(0)
			elif arg == '-h':
				args['help'] = True

		return args


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
		return len(self.args.input) > 0

	def run(self) -> None:
		"""実行処理"""
		parser = self.make_parser(self.args.parser)
		if self.args.help:
			self.run_help()
		elif self.args.input:
			self.run_parse(parser)
		else:
			self.run_interactive(parser)

	def run_help(self) -> None:
		"""実行処理(ヘルプ)"""
		print("""# Usage
$ bin/ast.sh [-i source_path] [-g grammar_path] [-p parser_name] [-h]
# Options
-i: Input source file
-g: Input grammar file
-p: Usage parser name (default="lark")
-h: Show help
# Examples
## Interactive mode
$ bin/ast.sh
$ bin/ast.sh -g path/to/grammar.lark
$ bin/ast.sh -g path/to/grammar.lark -p other
## Command line mode
$ bin/ast.sh -i path/to/source.py
$ bin/ast.sh -i path/to/source.py -g path/to/grammar.lark
$ bin/ast.sh -i path/to/source.py -g path/to/grammar.lark -p other
""")

	def run_parse(self, parser: Parser) -> None:
		"""実行処理(既存ファイルを解析)

		Args:
			parser: パーサー
		"""
		source = self.load_file(self.args.input)
		print(parser(source))

	def run_interactive(self, parser: Parser) -> None:
		"""実行処理(インタラクティブモード)

		Args:
			parser: パーサー
		"""
		while True:
			prompt = '\n'.join([
				'==========',
				'Code here. Type `exit` to quit:',
			])
			lines = tty(prompt)
			if len(lines) == 1 and lines[0] == 'exit':
				break

			try:
				text = '\n'.join(lines)
				ast = parser(f'{text}\n')
				print('==========')
				print('AST')
				print('----------')
				print(ast)
			except Exception as e:
				print(''.join(stacktrace(e)))

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
		grammar = self.load_file(self.args.grammar)
		if name == 'lark':
			parser = Lark(grammar, start='file_input', postlex=PythonIndenter(), parser='lalr')
			return lambda source: parser.parse(source).pretty()
		else:
			gram_parser = SyntaxParser(grammar_rules(), grammar_tokenizer())
			gram_ast = gram_parser.parse(grammar, 'entry')
			rules = Rules.from_ast(gram_ast.simplify())
			parser = SyntaxParser(rules)
			return lambda source: parser.parse(source, 'entry').pretty()


if __name__ == '__main__':
	args = Args(sys.argv[1:])
	app = App(args)
	try:
		app.run()
	except KeyboardInterrupt:
		pass
	except Exception as e:
		print(''.join(stacktrace(e)))
	finally:
		if not app.quiet:
			print('Quit')
