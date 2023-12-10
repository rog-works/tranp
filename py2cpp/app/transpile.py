import os
import sys

from lark import Lark, Tree, Token
from lark.indenter import PythonIndenter

from py2cpp.node.stringify import Stringify
from py2cpp.tp_lark.types import Entry


def appdir() -> str:
	return os.path.dirname(os.path.dirname(__file__))


def load_file(filename: str) -> str:
	filepath = os.path.join(appdir(), filename)
	with open(filepath) as f:
		return ''.join(f.readlines())


def dump(root: Entry):
	if type(root) is Tree:
		for child in root.children:
			dump(child)
	elif type(root) is Token:
		print(f'[{root.line}:{root.column}] {root.type} "{root.value}"')
	else:
		print('otherwise:', type(root), root)



def main(args: dict[str, str]):
	parser = Lark(load_file(args['grammar']), start='file_input', postlex=PythonIndenter(), parser='lalr')
	ast = parser.parse(load_file(args['source']))
	print('AST -----------------')
	print(ast.pretty())

	print('dump ----------------')
	dump(ast)
	print(Stringify(ast).flatten().join('').to_string())


if __name__ == '__main__':
	_, grammar_file, source_file = sys.argv
	main({'grammar': grammar_file, 'source': source_file})
