import os
import sys
import subprocess
import traceback
from typing import TypedDict

from lark import Lark
from lark.indenter import PythonIndenter

from py2cpp.bin.utils import appdir, readline

T_Options = TypedDict('T_Options', {'source': str, 'output': str})
T_Args = TypedDict('T_Args', {'runner': str, 'grammar': str, 'options': T_Options})


def load_file(filename: str) -> str:
	filepath = os.path.join(appdir(), filename)
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

	input_filepath = os.path.join(appdir(), 'bin/_input.sh')
	res = subprocess.run(['bash', input_filepath], stdout=subprocess.PIPE)
	return res.stdout.decode('utf-8').rstrip()


def run_interactive(parser: Lark) -> None:
	while True:
		proc(parser)

		ok = readline('exit? (y)es:')
		if ok == 'y':
			break


def run_parse(parser: Lark, source: str) -> None:
	print('file:', source)
	print('==========')
	print('AST')
	print('----------')
	print(parser.parse(load_file(source)).pretty())


def run_parse_to_save(parser: Lark, source: str, output: str) -> None:
	tree = parser.parse(load_file(source))
	pretty = '\n# '.join(tree.pretty().split('\n'))
	lines = [
		'from lark import Tree, Token',
		'def fixture() -> Tree:',
		f'	return {str(tree)}',
		'# ==========',
		f'# {pretty}',
	]
	with open(os.path.join(appdir(), output), mode='wb') as f:
		f.write(('\n'.join(lines)).encode('utf-8'))


def main(runner: str, grammar: str, options: T_Options) -> None:
	parser = Lark(load_file(grammar), start='file_input', postlex=PythonIndenter(), parser='lalr')

	if runner == 'interactive':
		run_interactive(parser)
	elif runner == 'file':
		run_parse(parser, options['source'])
	elif runner == 'output':
		run_parse_to_save(parser, options['source'], options['output'])


def parse_args(argv: list[str]) -> T_Args:
	runner = 'interactive'
	grammar = ''
	source = ''
	output = ''

	while(len(argv)):
		value = argv.pop(0)
		if value == '-i':
			runner = 'interactive'
		elif value == '-f':
			runner = 'file'
			source = argv.pop(0)
		elif value == '-g':
			grammar = argv.pop(0)
		elif value == '-o':
			runner = 'output'
			output = argv.pop(0)

	return {
		'runner': runner,
		'grammar': grammar,
		'options': {
			'source': source,
			'output': output,
		},
	}


if __name__ == '__main__':
	_, *argv = sys.argv
	main(**parse_args(argv))
