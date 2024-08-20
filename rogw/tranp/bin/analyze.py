import os
import sys
import json
from types import MethodType
from typing import Any, Callable, TypedDict, cast

from rogw.tranp.app.app import App
from rogw.tranp.bin.io import readline
from rogw.tranp.implements.cpp.providers.semantics import cpp_plugin_provider
from rogw.tranp.implements.syntax.lark.entry import EntryOfLark
from rogw.tranp.implements.syntax.lark.parser import SyntaxParserOfLark
from rogw.tranp.io.cache import CacheProvider
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.locator import Locator
from rogw.tranp.lang.module import fullyname
from rogw.tranp.module.modules import Modules
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.providers.module import module_path_dummy
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.semantics.reflection.db import SymbolDBProvider
from rogw.tranp.semantics.reflection.interface import IReflection
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.syntax.ast.entry import Entry
from rogw.tranp.syntax.ast.parser import ParserSetting, SyntaxParser
import rogw.tranp.syntax.node.definition as defs
from rogw.tranp.syntax.node.node import Node

ArgsDict = TypedDict('ArgsDict', {'grammar': str, 'input': str, 'options': dict[str, str]})


class Args:
	def __init__(self) -> None:
		args = self.__parse_argv(sys.argv[1:])
		self.grammar = args['grammar']
		self.input = args['input']
		self.options = args['options']

	def __parse_argv(self, argv: list[str]) -> ArgsDict:
		args: ArgsDict = {
			'grammar': 'data/grammar.lark',
			'input': 'example/example.py',
			'options': {},
		}
		while argv:
			arg = argv.pop(0)
			if arg == '-g':
				args['grammar'] = argv.pop(0)
			elif arg == '-i':
				args['input'] = argv.pop(0)
			elif arg.startswith('-'):
				args['options'][arg[1:]] = argv.pop(0)

		return args


def now() -> str:
	from datetime import datetime, timedelta, timezone

	zone = timezone(timedelta(hours=9), 'JST)')
	return datetime.now(zone).strftime('%Y-%m-%d %H:%M:%S')


@injectable
def make_parser_setting(args: Args) -> ParserSetting:
	return ParserSetting(grammar=args.grammar)


@injectable
def make_module_paths(args: Args) -> ModulePaths:
	basepath, extention = os.path.splitext(args.input)
	# XXX このスクリプトではLinux形式で入力する想定のためos.path.sepは使用しない
	return ModulePaths([ModulePath(basepath.replace('/', '.'), language=extention[1:])])


def fetch_main_entrypoint(modules: Modules, module_paths: ModulePaths) -> defs.Entrypoint:
	return modules.load(module_paths[0].path).entrypoint.as_a(defs.Entrypoint)


@injectable
def task_analyze(org_parser: SyntaxParser, cache: CacheProvider) -> None:
	def make_result() -> str:
		dummy_module_path = module_path_dummy()

		def new_parser(module_path: str) -> Entry:
			return root if module_path == dummy_module_path.path else org_parser(module_path)

		lark = cast(SyntaxParserOfLark, org_parser).dirty_get_origin()
		root = EntryOfLark(lark.parse(f'{"\n".join(lines)}\n'))
		difinitions = {
			fullyname(SyntaxParser): lambda: new_parser,
			fullyname(CacheProvider): lambda: cache,
		}
		return App(difinitions).resolve(Modules).load(dummy_module_path.path).entrypoint.pretty()

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

		ast = make_result()

		lines = [
			'==============',
			'AST',
			'--------------',
			ast,
			'--------------',
		]
		print('\n'.join(lines))

		if readline('(e)xit?:') == 'e':
			break


@injectable
def task_db(db_provider: SymbolDBProvider) -> None:
	title = '\n'.join([
		'==============',
		'Symbol DB',
		'--------------',
	])
	print(title)
	print(json.dumps([f'{key}: {raw.types.fullyname}' for key, raw in db_provider.db.items()], indent=2))


@injectable
def task_class(db_provider: SymbolDBProvider, reflections: Reflections) -> None:
	names = {raw.decl.fullyname: True for raw in db_provider.db.values() if raw.decl.is_a(defs.Class)}
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
	print(reflections.from_fullyname(name).types.pretty(1))


@injectable
def task_pretty(modules: Modules, module_paths: ModulePaths) -> None:
	entrypoint = fetch_main_entrypoint(modules, module_paths)
	title = '\n'.join([
		'==============',
		'AST',
		'--------------',
	])
	print(title)
	print(entrypoint.pretty())


@injectable
def task_symbol(modules: Modules, module_paths: ModulePaths, reflections: Reflections) -> None:
	while True:
		prompt = '\n'.join([
			'==============',
			'Node/Symbol fullyname or full_path or id here:',
		])
		name = readline(prompt)

		entrypoint = fetch_main_entrypoint(modules, module_paths)
		candidates = [node for node in entrypoint.procedural() if node.fullyname == name or node.full_path == name or str(node.id) == name]

		if len(candidates):
			node = candidates[0]
			symbol = reflections.type_of(node)

			print('--------------')
			print('Node')
			print('--------------')
			print(json.dumps(dump_node_data(node), indent=2))
			print('--------------')
			print('Type of')
			print('--------------')
			print(json.dumps(dump_symbol_data(symbol), indent=2))
			print('--------------')
		else:
			print('--------------')
			print('Not found')
			print('--------------')

		if readline('(e)xit?:') == 'e':
			break


def dump_node_data(node: Node) -> dict[str, Any]:
	data: dict[str, Any] = {}
	for key in dir(node):
		# FIXME constructorを安易にNullableにしたくないので一旦ガード節で対処
		if isinstance(node, defs.Class) and key == 'constructor':
			if not node.constructor_exists:
				continue

		attr = getattr(node, key)
		attr_type = type(attr)
		if not key.startswith('_') and attr_type is not MethodType:
			data[key] = str(attr) if attr_type is not list else list(map(str, attr))

			# XXX Class等はtokensが極端に長くなるため省略
			if key == 'tokens' and len(data[key]) > 50:
				data[key] = f'{data[key][:50]}...'

	return data


def dump_symbol_data(symbol: IReflection) -> dict[str, Any]:
	def attr_formatter(attr: IReflection) -> str:
		return f'{attr.__class__.__name__}:{str(attr)} at {str(attr.node or attr.decl)}'

	return {
		'types_full_path': symbol.types.full_path,
		'decl_full_path': symbol.decl.full_path,
		'shorthand': str(symbol),
		'types': str(symbol.types),
		'decl': str(symbol.decl),
		'node': str(symbol.node),
		'origin': attr_formatter(symbol.origin),
		'via': attr_formatter(symbol.via),
		'attrs': [attr_formatter(attr) for attr in symbol.attrs],
		'stacktrace': [attr_formatter(layer) for layer in symbol.stacktrace()],
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
		'* -i: Python source code input file path. default = "example/example.py"',
	]
	print('\n'.join(lines))


@injectable
def task_menu(locator: Locator) -> None:
	prompt = '\n'.join([
		'==============',
		'Task Menu',
		'--------------',
		'# Tasks',
		'* (a)nalyze : Interactive Syntax Analyzer',
		'* (c)lass   : Show Class Information',
		'* (d)b      : Show Symbol DB',
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
			fullyname(ModulePaths): make_module_paths,
			fullyname(ParserSetting): make_parser_setting,
			fullyname(PluginProvider): cpp_plugin_provider,
		}).run(task_menu)
	except KeyboardInterrupt:
		pass
	finally:
		print('Quit')
