import os
import sys
import json
from types import MethodType
from typing import Any, Callable, TypedDict, cast

from rogw.tranp.app.app import App
from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.bin.io import readline
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.annotation import duck_typed, injectable
from rogw.tranp.lang.locator import Invoker, Locator
from rogw.tranp.lang.module import filepath_to_module_path, fullyname
from rogw.tranp.module.modules import Modules
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.providers.module import module_path_dummy
from rogw.tranp.providers.syntax.ast import source_code_provider
from rogw.tranp.semantics.reflection.base import IReflection
from rogw.tranp.semantics.reflection.db import SymbolDB, SymbolDBFinalizer
from rogw.tranp.semantics.reflections import Reflections
from rogw.tranp.syntax.ast.parser import ParserSetting, SourceCodeProvider
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
			'input': '',
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
def make_module_paths(args: Args, loader: IFileLoader) -> ModulePaths:
	if not loader.exists(args.input):
		return ModulePaths([])

	basepath, extention = os.path.splitext(args.input)
	# XXX このスクリプトではLinux形式で入力する想定のためos.path.sepは使用しない
	return ModulePaths([ModulePath(basepath.replace('/', '.'), language=extention[1:])])


class Codes:
	@injectable
	def __init__(self, invoker: Invoker) -> None:
		self._org_codes = invoker(source_code_provider)
		self.source_code: str = ''

	@duck_typed(SourceCodeProvider)
	def __call__(self, module_path: str) -> str:
		if module_path == module_path_dummy().path:
			return f'{self.source_code}\n'
		else:
			return self._org_codes(module_path)


def fetch_main_entrypoint(modules: Modules, module_path: str) -> defs.Entrypoint:
	return modules.load(module_path).entrypoint.as_a(defs.Entrypoint)


@injectable
def task_analyze(locator: Locator) -> None:
	def make_result(source_code: str) -> str:
		module_path = module_path_dummy()
		codes = cast(Codes, locator.resolve(SourceCodeProvider))
		codes.source_code = source_code
		modules = locator.resolve(Modules)
		modules.unload(module_path.path)
		return modules.load(module_path.path).entrypoint.pretty()

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

		ast = make_result('\n'.join(lines))

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
def task_db(db: SymbolDB) -> None:
	title = '\n'.join([
		'==============',
		'Symbol DB',
		'--------------',
	])
	print(title)
	print(json.dumps([f'{key}: {raw.types.fullyname}' for key, raw in db.items()], indent=2))


@injectable
def task_class(db: SymbolDB, reflections: Reflections) -> None:
	names = {raw.decl.fullyname: True for raw in db.values() if raw.decl.is_a(defs.Class)}
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
def task_load(modules: Modules) -> None:
	filepath = readline('Module filepath here:')
	if not os.path.isabs(filepath):
		filepath = os.path.abspath(filepath)

	module_path = filepath_to_module_path(filepath, tranp_dir())
	modules.load(module_path)
	print('--------------')
	print('Module load completed!')


@injectable
def task_pretty(modules: Modules) -> None:
	prompt = '\n'.join([
		'==============',
		'Module List',
		'--------------',
		*[module.path for module in modules.loaded()],
		'--------------',
		'Module path here:',
	])
	module_path = readline(prompt)
	entrypoint = fetch_main_entrypoint(modules, module_path)
	title = '\n'.join([
		'==============',
		'AST',
		'--------------',
	])
	print(title)
	print(entrypoint.pretty())


@injectable
def task_symbol(modules: Modules, reflections: Reflections) -> None:
	prompt = '\n'.join([
		'==============',
		'Module List',
		'--------------',
		*[module.path for module in modules.loaded()],
		'--------------',
		'Module path here:',
	])
	module_path = readline(prompt)

	while True:
		prompt = '\n'.join([
			'==============',
			'Node/Symbol fullyname or full_path or id here:',
		])
		name = readline(prompt)

		entrypoint = fetch_main_entrypoint(modules, module_path)
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
def task_menu(invoker: Invoker, db_finalizer: SymbolDBFinalizer) -> None:
	# XXX シンボルテーブルを完成させるためコール
	db_finalizer()

	prompt = '\n'.join([
		'==============',
		'Task Menu',
		'--------------',
		'# Tasks',
		'* (a)nalyze : Interactive Syntax Analyzer',
		'* (c)lass   : Show Class Information',
		'* (d)b      : Show Symbol DB',
		'* (l)oad    : Load Module',
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
		'l': task_load,
		'p': task_pretty,
		's': task_symbol,
		'h': task_help,
	}
	while True:
		input = readline(prompt.replace('@now', now()))
		if input == 'q':
			return

		action = actions.get(input, task_help)
		invoker(action)


if __name__ == '__main__':
	try:
		App({
			fullyname(Args): Args,
			fullyname(ModulePaths): make_module_paths,
			fullyname(ParserSetting): make_parser_setting,
			fullyname(SourceCodeProvider): Codes,
		}).run(task_menu)
	except KeyboardInterrupt:
		pass
	finally:
		print('Quit')
