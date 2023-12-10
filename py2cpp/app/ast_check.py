import os
import sys
import traceback

from lark import Lark
from lark.indenter import PythonIndenter


def appdir() -> str:
	return os.path.dirname(os.path.dirname(__file__))


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


def main(args: dict[str, str]) -> None:
	parser = Lark(load_file(args['grammar']), start='file_input', postlex=PythonIndenter(), parser='lalr')

	while True:
		proc(parser)

		ok = input('exit? (y)es: ')
		if ok == 'y':
			break


if __name__ == '__main__':
	_, grammar_file = sys.argv
	main({'grammar': grammar_file})
