import os
import sys
import json
from typing import Any, Callable, cast

from py2cpp.analize.db import SymbolDB
from py2cpp.analize.symbols import Symbols
from py2cpp.app.app import App
from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import ParserSetting, SyntaxParser
from py2cpp.ast.query import Query
from py2cpp.bin.utils import readline
from py2cpp.lang.cache import CacheProvider
from py2cpp.lang.locator import Locator
from py2cpp.lang.module import fullyname
from py2cpp.module.types import ModulePath
import py2cpp.node.definition as defs
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


def now() -> str:
	from datetime import datetime, timedelta, timezone

	zone = timezone(timedelta(hours=9), 'JST)')
	return datetime.now(zone).strftime('%Y-%m-%d %H:%M:%S')


def make_parser_setting(args: Args) -> ParserSetting:
	return ParserSetting(grammar=args.grammar)


def make_module_path(args: Args) -> ModulePath:
	basepath, _ = os.path.splitext(args.source)
	module_path = basepath.replace('/', '.')
	return ModulePath('__main__', module_path)


def task_db(db: SymbolDB) -> None:
	title = '\n'.join([
		'==============',
		'Symbol DB',
		'--------------',
	])
	print(title)
	print(json.dumps([f'{key}: {raw.org_path}' for key, raw in db.raws.items()], indent=2))


def task_pretty(nodes: Query[Node]) -> None:
	title = '\n'.join([
		'==============',
		'AST',
		'--------------',
	])
	print(title)
	print(nodes.by('file_input').pretty())


def task_class(db: SymbolDB, symbols: Symbols) -> None:
	names = {raw.decl.fullyname: True for raw in db.raws.values() if raw.decl.is_a(defs.Class)}
	prompt = '\n'.join([
		'==============',
		'Class List',
		'--------------',
		*names.keys(),
		'--------------',
		'Class fullyname here:',
	])
	name = readline(prompt)
	print('--------------')
	print(symbols.from_fullyname(name).types.pretty(1))


def task_type(symbols: Symbols) -> None:
	prompt = '\n'.join([
		'==============',
		'Symbol fullyname here:',
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
		'$ bash bin/analize.sh [-g ${path}] [-s ${path}]',
		'# Options',
		'* -g: Grammar file path. defalut = "data/grammar.lark"',
		'* -s: Python sorce code file path. default = "example/example.py"',
	]
	print('\n'.join(lines))


def task_ast(org_parser: SyntaxParser, cache: CacheProvider) -> None:
	def make_result() -> tuple[str, str]:
		def new_parser(module_path: str) -> Entry:
			return root if module_path == '__main__' else org_parser(module_path)

		lark = cast(SyntaxParserOfLark, org_parser).dirty_get_origin()
		root = EntryOfLark(lark.parse(f'{"\n".join(lines)}\n'))
		new_difinitions = {fullyname(SyntaxParser): lambda: new_parser}
		org_definitions = {fullyname(CacheProvider): lambda: cache}
		app = App({**org_definitions, **new_difinitions})

		db = app.resolve(SymbolDB)
		symbols = app.resolve(Symbols)

		main_raws = {key: raw for key, raw in db.raws.items() if raw.decl.module_path == '__main__'}
		main_symbols = {key: str(symbols.from_fullyname(key)) for key, _ in main_raws.items()}
		found_symbols = '\n'.join([f'{key}: {symbol_type}' for key, symbol_type in main_symbols.items()])
		node = app.resolve(Query[Node]).by('file_input')
		return (found_symbols, node.pretty())

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

		symbols, ast = make_result()

		lines = [
			'==============',
			'Symbols',
			'--------------',
			symbols,
			'==============',
			'AST',
			'--------------',
			ast,
			'--------------',
		]
		print('\n'.join(lines))

		if readline('(e)xit?:') == 'e':
			break


def task_menu(locator: Locator) -> None:
	prompt = '\n'.join([
		'==============',
		'Task selection',
		'--------------',
		'# Tasks',
		'* (a)st    : Interactive AST Viewer',
		'* (p)retty : Show AST',
		'* (d)b     : Show Symbol DB',
		'* (c)lass  : Show Class Information',
		'* (t)ype   : Show Symbol Type',
		'* (h)elp   : Show Usage',
		'* (q)uit   : Quit',
		'--------------',
		'@now',
		'--------------',
		'here:',
	])
	actions: dict[str, Callable[..., None]] = {
		'a': task_ast,
		'p': task_pretty,
		'd': task_db,
		'c': task_class,
		't': task_type,
		'h': task_help,
	}
	while True:
		input = readline(prompt.replace('@now', now()))
		if input == 'q':
			return

		action = actions.get(input, task_help)
		locator.invoke(action)


if __name__ == '__main__':
	try:
		App({
			fullyname(Args): Args,
			fullyname(ParserSetting): make_parser_setting,
			fullyname(ModulePath): make_module_path,
		}).run(task_menu)
	except KeyboardInterrupt:
		pass
	finally:
		print('Quit')
