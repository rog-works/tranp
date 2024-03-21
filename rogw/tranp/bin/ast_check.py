import os
import sys
import subprocess
import traceback
from typing import TypedDict

from lark import Lark
from lark.indenter import PythonIndenter

from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.bin.io import readline

Options = TypedDict('Options', {'source': str})
Args = TypedDict('Args', {'runner': str, 'grammar': str, 'options': Options})


def load_file(filename: str) -> str:
	filepath = os.path.join(tranp_dir(), filename)
	with open(filepath) as f:
		return ''.join(f.readlines())


def proc(parser: Lark) -> None:
	print('python code here.')
	print('==========')

	lines: list[str] = []
	while True:
		line = readline()
		if not line:
			break

		lines.append(line)

	text = '\n'.join(lines)

	try:
		tree = parser.parse(f'{text}\n')
		print('==========')
		print('Dump')
		print('----------')
		print(str(tree))
		print('==========')
		print('AST')
		print('----------')
		print(tree.pretty())
	except Exception:
		print(traceback.format_exc())


def readline(prompt: str = '') -> str:
	if prompt:
		print(prompt)

	input_filepath = os.path.join(tranp_dir(), 'bin/_input.sh')
	res = subprocess.run(['bash', input_filepath], stdout=subprocess.PIPE)
	return res.stdout.decode('utf-8').rstrip()


def run_interactive(parser: Lark) -> None:
	while True:
		proc(parser)

		ok = readline('(e)xit?:')
		if ok == 'e':
			break


def run_parse(parser: Lark, source: str) -> None:
	print('file:', source)
	print('==========')
	print('AST')
	print('----------')
	print(parser.parse(load_file(source)).pretty())


def main(runner: str, grammar: str, options: Options) -> None:
	parser = Lark(load_file(grammar), start='file_input', postlex=PythonIndenter(), parser='lalr')

	if runner == 'interactive':
		run_interactive(parser)
	elif runner == 'file':
		run_parse(parser, options['source'])


def parse_args(argv: list[str]) -> Args:
	runner = 'interactive'
	grammar = ''
	source = ''

	while(len(argv)):
		value = argv.pop(0)
		if value == '-i':
			runner = 'interactive'
		elif value == '-f':
			runner = 'file'
			source = argv.pop(0)
		elif value == '-g':
			grammar = argv.pop(0)

	return {
		'runner': runner,
		'grammar': grammar,
		'options': {
			'source': source,
		},
	}


if __name__ == '__main__':
	try:
		_, *argv = sys.argv
		main(**parse_args(argv))
	except KeyboardInterrupt:
		pass
	finally:
		print('Quit')
