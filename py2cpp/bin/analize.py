import os
import sys
import json

from py2cpp.analize.db import SymbolDB
from py2cpp.analize.symbols import Symbols
from py2cpp.app.app import App
from py2cpp.ast.parser import ParserSetting
from py2cpp.lang.locator import Locator
from py2cpp.lang.module import fullyname
from py2cpp.module.types import ModulePath


class Args:
	def __init__(self) -> None:
		args = self.__parse_argv(sys.argv[1:])
		self.grammar = args['grammar']
		self.source = args['source']
		self.action = args['action']
		self.name = args['name']

	def __parse_argv(self, argv: list[str]) -> dict[str, str]:
		args = {
			'grammar': 'data/grammar.lark',
			'source': 'example/example.py',
			'action': 'db',
			'name': '',
		}
		while argv:
			arg = argv.pop(0)
			if arg == '-g':
				args['grammar'] = argv.pop(0)
			elif arg == '-s':
				args['source'] = argv.pop(0)
			elif arg == '-a':
				args['action'] = argv.pop(0)
			elif arg == '-n':
				args['name'] = argv.pop(0)

		return args


def make_parser_setting(args: Args) -> ParserSetting:
	return ParserSetting(grammar=args.grammar)


def make_module_path(args: Args) -> ModulePath:
	basepath, _ = os.path.splitext(args.source)
	module_path = basepath.replace('/', '.')
	return ModulePath('__main__', module_path)


def action_db(db: SymbolDB) -> None:
	print(json.dumps([f'{key}: {raw.org_path}' for key, raw in db.raws.items()], indent=2))


def action_type(args: Args, symbols: Symbols) -> None:
	print(f'{args.name}:', f'{symbols.from_fullyname(args.name)}')


def task(args: Args, locator: Locator) -> None:
	actions = {
		'db': action_db,
		'type': action_type,
	}
	locator.invoke(actions[args.action])


if __name__ == '__main__':
	App({
		fullyname(Args): Args,
		fullyname(ParserSetting): make_parser_setting,
		fullyname(ModulePath): make_module_path,
	}).run(task)
