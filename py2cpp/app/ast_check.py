import os
import sys
import traceback

from lark import Lark
from lark.indenter import PythonIndenter


def appdir() -> str:
	return os.path.join(os.path.dirname(__file__), '../../')


def load_file(filename: str) -> str:
	filepath = os.path.join(appdir(), filename)
	with open(filepath) as f:
		return ''.join(f.readlines())


def proc(parser: Lark) -> None:
	print('python code here.')
	print('==========')

	lines: list[str] = []
	while True:
		line = input()
		if not line:
			break

		lines.append(line)

	text = '\n'.join(lines)
	print('==========')
	print('AST')
	print('----------')
	try:
		print(parser.parse(f'{text}\n').pretty())
	except Exception:
		print(traceback.format_exc())


def run_interactive(parser: Lark) -> None:
	while True:
		proc(parser)

		ok = input('exit? (y)es: ')
		if ok == 'y':
			break


def run_parse(parser: Lark, source: str) -> None:
	print('file:', source)
	print('==========')
	print('AST')
	print('----------')
	print(parser.parse(load_file(source)).pretty())


def main(runner: str, grammar: str, source: str) -> None:
	parser = Lark(load_file(grammar), start='file_input', postlex=PythonIndenter(), parser='lalr')

	if runner == 'interactive':
		run_interactive(parser)
	elif runner == 'file':
		run_parse(parser, source)


def parse_args(argv: list[str]) -> dict[str, str]:
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
		'source': source,
	}


if __name__ == '__main__':
	_, *argv = sys.argv
	main(**parse_args(argv))
