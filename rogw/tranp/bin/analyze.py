import os
import sys
import json
from types import MethodType
from typing import Any, Callable, cast

from rogw.tranp.app.app import App
from rogw.tranp.bin.io import readline
import rogw.tranp.compatible.python.classes as classes
from rogw.tranp.errors import LogicError
from rogw.tranp.implements.cpp.providers.semantics import cpp_plugin_provider
from rogw.tranp.implements.syntax.lark.entry import EntryOfLark
from rogw.tranp.implements.syntax.lark.parser import SyntaxParserOfLark
from rogw.tranp.io.cache import CacheProvider
from rogw.tranp.lang.locator import Locator
from rogw.tranp.lang.module import fullyname
from rogw.tranp.module.module import Module
from rogw.tranp.module.types import ModulePath
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.semantics.reflection import IReflection, SymbolDB
from rogw.tranp.semantics.symbols import Symbols
from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.syntax.ast.parser import ParserSetting, SyntaxParser
from rogw.tranp.syntax.ast.query import Query
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node


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
	print(json.dumps([f'{key}: {raw.org_fullyname}' for key, raw in db.raws.items()], indent=2))


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


def task_symbol(symbols: Symbols) -> None:
	prompt = '\n'.join([
		'==============',
		'Symbol fullyname here:',
	])
	name = readline(prompt)

	symbol = symbols.from_fullyname(name)

	print('--------------')
	print(json.dumps(dump_symbol_data(symbol), indent=2))


def task_node(module: Module, symbols: Symbols) -> None:
	prompt = '\n'.join([
		'==============',
		'Node fullyname here:',
	])
	name = readline(prompt)

	candidates = [node for node in module.entrypoint.flatten() if node.fullyname == name]

	if len(candidates):
		node = candidates[0]
		symbol = symbols.type_of(node)

		print('--------------')
		print('Node')
		print('--------------')
		print(json.dumps(dump_node_data(node), indent=2))
		print('--------------')
		print('Type of')
		print('--------------')
		print(json.dumps(dump_symbol_data(symbol), indent=2))
	else:
		print('--------------')
		print('Not found')


def dump_node_data(node: Node) -> dict[str, Any]:
	data: dict[str, Any] = {}
	for key in dir(node):
		attr = getattr(node, key)
		attr_type = type(attr)
		if not key.startswith('_') and attr_type is not MethodType:
			data[key] = str(attr) if attr_type is not list else list(map(str, attr))

	return data


def dump_symbol_data(symbol: IReflection) -> dict[str, Any]:
	return {
		'types_full_path': symbol.types.full_path,
		'decl_full_path': symbol.decl.full_path,
		'shorthand': str(symbol),
		'ref_fullyname': symbol.ref_fullyname,
		'org_fullyname': symbol.org_fullyname,
		'types': str(symbol.types),
		'decl': str(symbol.decl),
		'origin': str(symbol.origin),
		'attrs': [str(attr) for attr in symbol.attrs],
		'hierarchy': [f'{layer.__class__.__name__} -> {str(layer.via or layer.decl)}' for layer in symbol.hierarchy()],
	}


def task_help() -> None:
	lines = [
		'==============',
		'Help',
		'--------------',
		'# Usage',
		'$ bash bin/analyze.sh [-g ${path}] [-s ${path}]',
		'# Options',
		'* -g: Grammar file path. defalut = "data/grammar.lark"',
		'* -s: Python sorce code file path. default = "example/example.py"',
	]
	print('\n'.join(lines))


def task_analyze(org_parser: SyntaxParser, cache: CacheProvider) -> None:
	def make_result() -> tuple[str, str]:
		def new_parser(module_path: str) -> Entry:
			return root if module_path == '__main__' else org_parser(module_path)

		def resolve_symbol(symbols: Symbols, name: str) -> IReflection:
			try:
				return symbols.from_fullyname(name)
			except LogicError:
				return symbols.type_of_standard(classes.Unknown)

		lark = cast(SyntaxParserOfLark, org_parser).dirty_get_origin()
		root = EntryOfLark(lark.parse(f'{"\n".join(lines)}\n'))
		new_difinitions = {fullyname(SyntaxParser): lambda: new_parser}
		org_definitions = {fullyname(CacheProvider): lambda: cache}
		app = App({**org_definitions, **new_difinitions})

		db = app.resolve(SymbolDB)
		symbols = app.resolve(Symbols)

		main_raws = {key: raw for key, raw in db.raws.items() if raw.decl.module_path == '__main__'}
		main_symbols = {key: str(resolve_symbol(symbols, key)) for key, _ in main_raws.items()}
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
		'Task Menu',
		'--------------',
		'# Tasks',
		'* (a)nalyze : Interactive Syntax Analyzer',
		'* (c)lass   : Show Class Information',
		'* (d)b      : Show Symbol DB',
		'* (n)ode    : Analyze Node',
		'* (p)retty  : Show AST',
		'* (s)ymbol  : Show Symbol Information',
		'* (h)elp    : Show Usage',
		'* (q)uit    : Quit',
		'--------------',
		'@@now',
		'--------------',
		'Selection here:',
	])
	actions: dict[str, Callable[..., None]] = {
		'a': task_analyze,
		'c': task_class,
		'd': task_db,
		'n': task_node,
		'p': task_pretty,
		's': task_symbol,
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
			fullyname(PluginProvider): cpp_plugin_provider,
		}).run(task_menu)
	except KeyboardInterrupt:
		pass
	finally:
		print('Quit')
