import os
import sys
import json
from typing import Any, cast

from py2cpp.analize.db import SymbolDB
from py2cpp.analize.symbols import Symbols
from py2cpp.app.app import App
from py2cpp.ast.parser import ParserSetting, SyntaxParser
from py2cpp.ast.query import Query
from py2cpp.bin.utils import readline
from py2cpp.lang.locator import Locator
from py2cpp.lang.module import fullyname
from py2cpp.module.types import ModulePath
from py2cpp.node.node import Node
from py2cpp.tp_lark.entry import EntryOfLark
from py2cpp.tp_lark.parser import SyntaxParserOfLark


class Args:
	def __init__(self) -> None:
		args = self.__parse_argv(sys.argv[1:])
		self.grammar = args['grammar']
		self.source = args['source']
		self.options = args['options']

	def __parse_argv(self, argv: list[str]) -> dict[str, Any]:
		args = {
			'grammar': 'data/grammar.lark',
			'source': 'example/example.py',
			'options': {},
		}
		while argv:
			arg = argv.pop(0)
			if arg == '-g':
				args['grammar'] = argv.pop(0)
			elif arg == '-s':
				args['source'] = argv.pop(0)
			elif arg.startswith('-'):
				args['options'][arg[1:]] = argv.pop(0)

		return args


def make_parser_setting(args: Args) -> ParserSetting:
	return ParserSetting(grammar=args.grammar)


def make_module_path(args: Args) -> ModulePath:
	basepath, _ = os.path.splitext(args.source)
	module_path = basepath.replace('/', '.')
	return ModulePath('__main__', module_path)


def task_db(db: SymbolDB) -> None:
	print(json.dumps([f'{key}: {raw.org_path}' for key, raw in db.raws.items()], indent=2))


def task_type(symbols: Symbols) -> None:
	prompt = '\n'.join([
		'==============',
		'Symbol name here:',
	])
	name = readline(prompt)
	print('--------------')
	print(f'{name}:', f'{str(symbols.from_fullyname(name))}')


def task_help() -> None:
	lines = [
		'==============',
		'Help',
		'--------------',
		'# Usage',
		'$ bash bin/analize.sh -g ${path} -s ${path}',
		'# Options',
		'* -g: Grammar file path',
		'* -s: Python sorce code file path',
	]
	print('\n'.join(lines))


def task_ast(parser: SyntaxParser) -> None:
	while True:
		title = '\n'.join([
			'==============',
			'Python code here:'
		])
		print(title)

		lines: list[str] = []
		while True:
			line = readline()
			if not line:
				break

			lines.append(line)

		org_parser = cast(SyntaxParserOfLark, parser).dirty_get_origin()
		root = EntryOfLark(org_parser.parse(f'{"\n".join(lines)}\n'))
		new_parser: SyntaxParser = lambda module_path: root
		node = App({fullyname(SyntaxParser): lambda: new_parser}).resolve(Query[Node]).by('file_input')

		print('--------------')
		print(node.pretty())
		print('--------------')

		if readline('(e)xit?:') == 'e':
			break


def task_menu(locator: Locator) -> None:
	prompt = '\n'.join([
		'==============',
		'Task selection',
		'--------------',
		'# Tasks',
		'* (a)st  : Interactive AST Viewer',
		'* (d)b   : Show Symbol DB',
		'* (t)ype : Show Symbol Type',
		'* (h)elp : Show Usage',
		'* (q)uit : Quit',
		'--------------',
		'here:',
	])
	actions = {
		'a': task_ast,
		'd': task_db,
		't': task_type,
		'h': task_help,
	}
	while True:
		input = readline(prompt)
		if input in ['quit', 'q']:
			return

		action = actions.get(input, 'help')
		locator.invoke(action)

		print('--------------')
		readline('Next... Enter here:')


if __name__ == '__main__':
	App({
		fullyname(Args): Args,
		fullyname(ParserSetting): make_parser_setting,
		fullyname(ModulePath): make_module_path,
	}).run(task_menu)
