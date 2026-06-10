import os
import sys
from typing import TypedDict

from data.syntax.rules_gram import grammar_rules, grammar_tokenizer
from rogw.tranp.bin.io import tty
from rogw.tranp.implements.syntax.tranp.ast import ASTTree
from rogw.tranp.implements.syntax.tranp.rule import Rules
from rogw.tranp.implements.syntax.tranp.syntax import SyntaxParser
from rogw.tranp.lang.error import stacktrace

DictArgs = TypedDict('DictArgs', {'input': str, 'output': str, 'help': bool})


class Args:
	"""アプリケーション引数"""

	def __init__(self, argv: list[str]) -> None:
		"""インスタンスを生成

		Args:
			argv: コマンドライン引数
		"""
		args = self.parse(argv)
		self.input = args['input']
		self.output = args['output']
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
			'output': '',
			'help': False,
		}
		while(len(argv)):
			value = argv.pop(0)
			if value == '-i':
				args['input'] = argv.pop(0)
			elif value == '-o':
				args['output'] = argv.pop(0)
			elif value == '-h':
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
		self.parser = SyntaxParser(grammar_rules(), grammar_tokenizer())

	@property
	def quiet(self) -> bool:
		"""Returns: True = 実行ログなし"""
		return len(self.args.input) > 0

	def run(self) -> None:
		"""実行処理"""
		if self.args.help:
			self.run_help()
		elif self.args.output:
			self.run_output()
		elif self.args.input:
			self.run_echo()
		else:
			self.run_interactive()

	def run_help(self) -> None:
		"""実行処理(ヘルプ)"""
		print("""# Usage
$ bin/gram.sh [-i grammar_path] [-o output_path] [-h]
# Options
-i: Input grammar file
-o: Output rules file
-h: Show help
# Examples
## Interactive mode
$ bin/gram.sh
## Command line mode
$ bin/gram.sh -i path/to/grammar.lark
$ bin/gram.sh -i path/to/grammar.lark -o path/to/output_rules.py
""")

	def run_echo(self) -> None:
		"""実行処理(解析結果を標準出力)"""
		source = self.load_source(self.args.input)
		tree = self.parser.parse(source, 'entry')
		# XXX 制御コードにエスケープを付与
		print('\\\\'.join(tree.pretty('\t').split('\\')))

	def run_output(self) -> None:
		"""実行処理(ルールリストをファイル出力)"""
		source = self.load_source(self.args.input)
		tree = self.parser.parse(source, 'entry')
		with open(self.args.output, mode='w') as f:
			f.write(self.render_rules(tree))

	def render_rules(self, tree: ASTTree) -> str:
		"""ルールリストをレンダリング

		Args:
			tree: ASTツリー
		Returns:
			結果
		"""
		ast = '\n\t'.join(tree.pretty('\t').split('\n'))
		ast = '\\\\'.join(ast.split('\\'))
		filename, _ = os.path.splitext(os.path.basename(self.args.output))
		return f"""from {Rules.__module__} import {Rules.__name__}

def {filename}() -> {Rules.__name__}:
	return {Rules.__name__}.{Rules.from_ast.__name__}({ast})
"""

	def run_interactive(self) -> None:
		"""実行処理(インタラクティブモード)"""
		while True:
			prompt = '\n'.join([
				'==========',
				'Grammar code here. Type `exit` to quit:',
			])
			lines = tty(prompt)
			if len(lines) == 1 and lines[0] == 'exit':
				break

			try:
				text = '\n'.join(lines)
				tree = self.parser.parse(f'{text}\n', 'entry')
				print('==========')
				print('AST')
				print('----------')
				print(tree.pretty())
			except Exception as e:
				print(''.join(stacktrace(e)))

	def load_source(self, filepath: str) -> str:
		"""ソースコードを読み込み

		Args:
			args: 引数
		Returns:
			テキスト
		"""
		fullpath = os.path.abspath(os.path.join(os.getcwd(), filepath))
		with open(fullpath, mode='rb') as f:
			return f.read().decode('utf-8')


if __name__ == '__main__':
	app = App(Args(sys.argv[1:]))
	try:
		app.run()
	except KeyboardInterrupt:
		pass
	except Exception as e:
		print(''.join(stacktrace(e)))
	finally:
		if not app.quiet:
			print('Quit')
