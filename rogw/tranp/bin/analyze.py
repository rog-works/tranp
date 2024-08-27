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

ArgsDict = TypedDict('ArgsDict', {'grammar': str, 'input': str, 'command': str, 'options': dict[str, str]})


class Args:
	"""コマンドライン引数"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		args = self.__parse_argv(sys.argv[1:])
		self.grammar = args['grammar']
		self.input = args['input']
		self.command = args['command']
		self.options = args['options']

	def __parse_argv(self, argv: list[str]) -> ArgsDict:
		"""コマンドライン引数を解析

		Args:
			argv (list[str]): 引数リスト
		Returns:
			ArgsDict: コマンドライン引数のデータ
		"""
		args: ArgsDict = {
			'grammar': 'data/grammar.lark',
			'input': '',
			'command': '',
			'options': {},
		}
		while argv:
			arg = argv.pop(0)
			if arg == '-g':
				args['grammar'] = argv.pop(0)
			elif arg == '-i':
				args['input'] = argv.pop(0)
			elif arg == '-c':
				args['command'] = argv.pop(0)
			elif arg.startswith('--'):
				args['options'][arg[2:]] = argv.pop(0)

		return args


class Codes:
	"""偽装ソースコードプロバイダー"""

	@injectable
	def __init__(self, invoker: Invoker) -> None:
		"""インスタンスを生成

		Args:
			invoker (Invoker): ファクトリー関数 @inject
		"""
		self._org_codes = invoker(source_code_provider)
		self.source_code: str = ''

	@duck_typed(SourceCodeProvider)
	def __call__(self, module_path: str) -> str:
		"""モジュールパスを基にソースコードを生成

		Args:
			module_path (str): モジュールパス
		Returns:
			str: ソースコード
		"""
		if module_path == module_path_dummy().path:
			return f'{self.source_code}\n'
		else:
			return self._org_codes(module_path)


class AnalyzeApp(App):
	"""アナライザーアプリケーション"""

	@classmethod
	@injectable
	def make_parser_setting(cls, args: Args) -> ParserSetting:
		"""シンタックスパーサー設定データを生成

		Args:
			args (Args): コマンドライン引数 @inject
		Returns:
			ParserSetting: シンタックスパーサー設定
		"""
		return ParserSetting(grammar=args.grammar)

	@classmethod
	@injectable
	def make_module_paths(cls, args: Args, loader: IFileLoader) -> ModulePaths:
		"""処理対象のモジュールパスリストを生成

		Args:
			args (Args): コマンドライン引数 @inject
			loader (IFileLoader): ファイルローダー @inject
		Returns:
			ModulePaths: 処理対象のモジュールパスリスト
		"""
		if not loader.exists(args.input):
			return ModulePaths([])

		basepath, extention = os.path.splitext(args.input)
		# XXX このスクリプトではLinux形式で入力する想定のためos.path.sepは使用しない
		return ModulePaths([ModulePath(basepath.replace('/', '.'), language=extention[1:])])

	@property
	def now(self) -> str:
		"""str: 現在時刻"""
		from datetime import datetime, timedelta, timezone

		zone = timezone(timedelta(hours=9), 'JST)')
		return datetime.now(zone).strftime('%Y-%m-%d %H:%M:%S')

	def fetch_entrypoint(self, module_path: str) -> defs.Entrypoint:
		"""モジュールのエントリーポイントを取得

		Args:
			module_path (str): モジュールパス
		Returns:
			Entrypoint: エントリーポイントノード
		"""
		return self.resolve(Modules).load(module_path).entrypoint.as_a(defs.Entrypoint)

	def serialize_db(self) -> dict[str, str]:
		"""シンボルテーブルをシリアライズ

		Returns:
			dict[str, str]: データ
		"""
		return {key: raw.types.fullyname for key, raw in self.resolve(SymbolDB).items()}

	def serialize_classes(self) -> list[str]:
		"""シンボルテーブル内の全てのクラスをシリアライズ

		Returns:
			list[str]: データ
		"""
		return [raw.decl.fullyname for raw in self.resolve(SymbolDB).values() if raw.decl.is_a(defs.Class)]

	def serialize_class(self, types: defs.ClassDef) -> str:
		"""シンボル定義ノードをシリアライズ

		Args:
			types (ClassDef): シンボル定義ノード
		Returns:
			str: データ
		"""
		return types.pretty(1)

	def serialize_modules(self) -> list[str]:
		"""全てのモジュールをシリアライズ

		Returns:
			list[str]: データ
		"""
		return [module.path for module in self.resolve(Modules).loaded()]

	def serialize_node(self, node: Node) -> dict[str, Any]:
		"""ノードをシリアライズ

		Args:
			node (Node): ノード
		Returns:
			dict[str, Any]: データ
		"""
		symbol = self.resolve(Reflections).type_of(node)
		return {
			'Node': self.dump_node(node),
			'Symbol': self.dump_symbol(symbol),
		}

	def dump_node(self, node: Node) -> dict[str, Any]:
		"""ノードをダンプ

		Args:
			node (Node): ノード
		Returns:
			dict[str, Any]: データ
		"""
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

	def dump_symbol(self, symbol: IReflection) -> dict[str, Any]:
		"""シンボルをダンプ

		Args:
			symbol (IReflection): シンボル
		Returns:
			dict[str, Any]: データ
		"""
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

	def task_analyze(self) -> None:
		"""タスク(インタラクティブ解析)"""
		def make_result(source_code: str) -> str:
			locator = self.resolve(Locator)
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

	def task_db(self) -> None:
		"""タスク(シンボルテーブル表示)"""
		title = '\n'.join([
			'==============',
			'Symbol DB',
			'--------------',
		])
		print(title)
		print(json.dumps(self.serialize_db(), indent=2))

	def task_class(self) -> None:
		"""タスク(クラス表示)"""
		prompt = '\n'.join([
			'==============',
			'Class List',
			'--------------',
			*self.serialize_classes(),
			'--------------',
			'Class fullyname here:',
		])
		name = readline(prompt)

		print('--------------')
		print(self.serialize_class(self.resolve(Reflections).from_fullyname(name).types))

	def task_load(self) -> None:
		"""タスク(モジュールロード)"""
		filepath = readline('Module filepath here:')
		if not os.path.isabs(filepath):
			filepath = os.path.abspath(filepath)

		module_path = filepath_to_module_path(filepath, tranp_dir())
		self.resolve(Modules).load(module_path)
		print('--------------')
		print('Module load completed!')

	def task_pretty(self) -> None:
		"""タスク(ノード階層表示)"""
		prompt = '\n'.join([
			'==============',
			'Module List',
			'--------------',
			*self.serialize_modules(),
			'--------------',
			'Module path here:',
		])
		module_path = readline(prompt)

		entrypoint = self.fetch_entrypoint(module_path)
		title = '\n'.join([
			'==============',
			'AST',
			'--------------',
		])
		print(title)
		print(entrypoint.pretty())

	def task_symbol(self) -> None:
		"""タスク(シンボル詳細表示)"""
		prompt = '\n'.join([
			'==============',
			'Module List',
			'--------------',
			*self.serialize_modules(),
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

			entrypoint = self.fetch_entrypoint(module_path)
			candidates = [node for node in entrypoint.procedural() if node.fullyname == name or node.full_path == name or str(node.id) == name]

			if len(candidates):
				print(json.dumps(self.serialize_node(candidates[0]), indent=2))
			else:
				print('--------------')
				print('Not found')
				print('--------------')

			if readline('(e)xit?:') == 'e':
				break

	def task_help(self) -> None:
		"""タスク(ヘルプ表示)"""
		lines = [
			'==============',
			'Help',
			'--------------',
			'# Usage',
			'$ bash bin/analyze.sh [-g ${filepath}] [-i ${filepath}] [-c [classes] [class --name ${name}] [db] [modules] [pretty --module ${module}] [symbol --name ${name}]]',
			'# Options',
			'* -g: Grammar file path. defalut = "data/grammar.lark"',
			'* -i: Python source code input file path. default = ""',
			'* -c: Execute command. classes | class | db | modules | pretty | symbol',
			'# Command options',
			'* -module: Module path',
			'* -name: Node fullyname',
			'# Commands',
			'* classes: Show class list',
			'* class: Show class description',
			'* db: Show symbol list',
			'* modules: Show module list',
			'* pretty: Show node ast',
			'* symbol: Show symbol description',
		]
		print('\n'.join(lines))

	@injectable
	def task_menu(self) -> None:
		"""タスク(メニュー選択)"""
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
			'a': self.task_analyze,
			'c': self.task_class,
			'd': self.task_db,
			'l': self.task_load,
			'p': self.task_pretty,
			's': self.task_symbol,
			'h': self.task_help,
		}
		try:
			while True:
				input = readline(prompt.replace('@now', self.now))
				if input == 'q':
					return

				action = actions.get(input, self.task_help)
				action()
		except KeyboardInterrupt:
			pass
		finally:
			print('Quit')

	def show_classes(self) -> None:
		"""表示(クラス一覧)"""
		print('\n'.join(self.serialize_classes()))

	def show_class(self, fullyname: str) -> None:
		"""表示(クラス詳細)

		Args:
			fullyname (str): 完全参照名
		"""
		print(self.serialize_class(self.resolve(Reflections).from_fullyname(fullyname).types))

	def show_db(self) -> None:
		"""表示(シンボルテーブル)"""
		print('\n'.join(self.serialize_db()))

	def show_modules(self) -> None:
		"""表示(モジュール一覧)"""
		print('\n'.join(self.serialize_modules()))

	def show_pretty(self, module_path: str) -> None:
		"""表示(ノード階層)

		Args:
			module_path (str): モジュールパス
		"""
		print(self.fetch_entrypoint(module_path).pretty())

	def show_symbol(self, fullyname: str) -> None:
		"""表示(シンボル詳細)

		Args:
			fullyname (str): 完全参照名
		"""
		symbol = self.resolve(Reflections).from_fullyname(fullyname)
		print(json.dumps(self.serialize_node(symbol.types), indent=2))

	@injectable
	def main(self, args: Args, db_finalizer: SymbolDBFinalizer) -> None:
		"""アプリケーションのエントリーポイント

		Args:
			args (Args): コマンドライン引数
			db_finalizer (SymbolDBFinalizer): シンボルテーブル完成プロセス
		"""
		# XXX シンボルテーブルを完成させるためコール
		db_finalizer()

		if len(args.command) == 0:
			self.task_menu()
			return

		actions = {
			'classes': lambda: self.show_classes(),
			'class': lambda: self.show_class(args.options.get('name', '')),
			'db': lambda: self.show_db(),
			'modules': lambda: self.show_modules(),
			'pretty': lambda: self.show_pretty(args.options.get('module', '')),
			'symbol': lambda: self.show_symbol(args.options.get('name', '')),
		}
		action = actions.get(args.command, self.task_help)
		action()


if __name__ == '__main__':
	app = AnalyzeApp({
		fullyname(Args): Args,
		fullyname(ModulePaths): AnalyzeApp.make_module_paths,
		fullyname(ParserSetting): AnalyzeApp.make_parser_setting,
		fullyname(SourceCodeProvider): Codes,
	})
	app.run(app.main)
