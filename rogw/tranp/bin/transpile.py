import os
import re
import sys
from typing import Any, Literal, TypedDict, cast

import yaml

from rogw.tranp.app.app import App
from rogw.tranp.app.dummy import WrapSourceProvider, make_dummy_module_meta_factory
from rogw.tranp.bin.io import readline
from rogw.tranp.data.meta.header import MetaHeader
from rogw.tranp.data.meta.types import ModuleMetaFactory
from rogw.tranp.file.loader import IDataLoader, ISourceLoader
from rogw.tranp.file.writer import Writer
from rogw.tranp.i18n.i18n import I18n, TranslationMapping
from rogw.tranp.implements.cpp.providers.semantics import plugin_provider_cpp
from rogw.tranp.implements.cpp.providers.view import renderer_helper_provider_cpp
from rogw.tranp.implements.cpp.transpiler.py2cpp import Py2Cpp
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.convertion import as_a
from rogw.tranp.lang.di import DI, ModuleDefinitions
from rogw.tranp.lang.error import stacktrace
from rogw.tranp.lang.locator import Invoker, Locator
from rogw.tranp.lang.module import to_fullyname, module_path_to_filepath
from rogw.tranp.lang.profile import profiler
from rogw.tranp.module.includer import include_module_paths
from rogw.tranp.module.module import Module
from rogw.tranp.module.modules import Modules
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.syntax.ast.parser import ParserSetting, SourceProvider
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.transpiler.types import ITranspiler, TranspilerOptions
from rogw.tranp.view.render import Renderer, RendererHelperProvider, RendererSetting

ArgsDict = TypedDict('ArgsDict', {
	'config': str,
	'force': bool,
	'verbose': bool,
	'profile': bool,
	'interactive': bool,
})
EnvDict = TypedDict('EnvDict', {
	'transpiler': dict[str, Any],
	'view': dict[str, Any],
})
ConfigDict = TypedDict('ConfigDict', {
	'grammar': str,
	'template_dirs': list[str],
	'trans_mapping': str,
	'input_globs': list[str],
	'exclude_patterns': list[str],
	'output_dirs': list[str],
	'output_language': str,
	'di': dict[str, str],
	'env': EnvDict,
	'force': bool,
	'verbose': bool,
	'profile': bool,
	'interactive': bool,
})


class Config:
	"""コンフィグ"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		args = self.__parse_argv(sys.argv[1:])
		config = self.__load_config(args['config'])
		self.grammar = config['grammar']
		self.template_dirs = config['template_dirs']
		self.trans_mapping = config['trans_mapping']
		self.input_globs = config['input_globs']
		self.exclude_patterns = config['exclude_patterns']
		self.output_dirs = config['output_dirs']
		self.output_language = config['output_language']
		self.di = config.get('di', {})
		self.env = config.get('env', {})
		self.force = config.get('force', args['force'])
		self.verbose = config.get('verbose', args['verbose'])
		self.profile = config.get('profile', args['profile'])
		self.mode: Literal['runner', 'interactive'] = 'interactive' if config.get('interactive', args['interactive']) else 'runner'

	def __load_config(self, filepath: str) -> ConfigDict:
		"""コマンド引数をパース

		Args:
			filepath (str): コンフィグファイルのパス
		Returns:
			ConfigDict: コンフィグデータ
		"""
		with open(os.path.join(filepath)) as f:
			return cast(ConfigDict, yaml.safe_load(f))

	def __parse_argv(self, argv: list[str]) -> ArgsDict:
		"""コマンド引数をパース

		Args:
			argv (list[str]): コマンド引数リスト
		Returns:
			ArgsDict: パースしたコマンド引数
		"""
		args: ArgsDict = {
			'config': 'example/config.yml',
			'force': False,
			'verbose': False,
			'profile': False,
			'interactive': False,
		}
		while argv:
			arg = argv.pop(0)
			if arg == '-c':
				args['config'] = argv.pop(0)
			elif arg == '-f':
				args['force'] = True
			elif arg == '-v':
				args['verbose'] = True
			elif arg == '-p':
				args['profile'] = True
			elif arg == '-i':
				args['interactive'] = True

		return args


class TranspileApp:
	"""トランスパイルアプリケーション"""

	@classmethod
	@injectable
	def make_renderer_setting(cls, config: Config, i18n: I18n) -> RendererSetting:
		"""テンプレートレンダーを生成

		Args:
			config (Config): コンフィグ @inject
			i18n (I18n): 国際化対応モジュール @inject
		Returns:
			Renderer: テンプレートレンダー
		"""
		return RendererSetting(config.template_dirs, i18n.t, config.env['view'])

	@classmethod
	@injectable
	def make_options(cls, config: Config) -> TranspilerOptions:
		"""トランスパイルオプションを生成

		Args:
			config (Config): コンフィグ @inject
		Returns:
			TranspilerOptions: トランスパイルオプション
		"""
		return TranspilerOptions(verbose=config.verbose, env=config.env['transpiler'])

	@classmethod
	@injectable
	def make_parser_setting(cls, config: Config) -> ParserSetting:
		"""シンタックスパーサー設定データを生成

		Args:
			config (Config): コンフィグ @inject
		Returns:
			ParserSetting: シンタックスパーサー設定データ
		"""
		return ParserSetting(grammar=config.grammar)

	@classmethod
	@injectable
	def make_translation_mapping(cls, datums: IDataLoader, config: Config) -> TranslationMapping:
		"""翻訳マッピングデータを生成

		Args:
			datums (IDataLoader): データローダー @inject
			config (Config): コンフィグ @inject
		Returns:
			TranslationMapping: 翻訳マッピングデータ
		"""
		mapping = cast(dict[str, str], yaml.safe_load(datums.load(config.trans_mapping)))
		return TranslationMapping(to=mapping)

	@classmethod
	@injectable
	def make_module_paths(cls, config: Config) -> ModulePaths:
		"""モジュールパスリストを生成

		Args:
			config (Config): コンフィグ @inject
		Returns:
			ModulePaths: モジュールパスリスト
		"""
		module_paths = ModulePaths()
		for input_glob in config.input_globs:
			module_paths.extend(include_module_paths(input_glob, config.exclude_patterns))

		return module_paths

	@classmethod
	def definitions(cls) -> ModuleDefinitions:
		"""モジュール定義を生成

		Returns:
			ModuleDefinitions: モジュール定義
		"""
		config = Config()
		definitions = {
			to_fullyname(Config): lambda: config,
			to_fullyname(ITranspiler): Py2Cpp,
			to_fullyname(ModulePaths): cls.make_module_paths,
			to_fullyname(ParserSetting): cls.make_parser_setting,
			to_fullyname(PluginProvider): plugin_provider_cpp,  # FIXME C++固定
			to_fullyname(Renderer): Renderer,
			to_fullyname(RendererHelperProvider): renderer_helper_provider_cpp,
			to_fullyname(RendererSetting): cls.make_renderer_setting,
			to_fullyname(TranslationMapping): cls.make_translation_mapping,
			to_fullyname(TranspilerOptions): cls.make_options,
		}
		return {**definitions, **config.di}

	@classmethod
	@injectable
	def run(cls, invoker: Invoker, config: Config) -> None:
		"""アプリケーションの実行処理

		Args:
			invoker (Invoker): ファクトリー関数
			config (Config): コンフィグ
		"""
		modes = {
			'runner': Runner,
			'interactive': Interactive,
		}
		invoker(modes[config.mode]).exec()


class Runner:
	"""ランナー(非対話モード)"""

	def __init__(self, sources: ISourceLoader, config: Config, module_paths: ModulePaths, modules: Modules, module_meta_factory: ModuleMetaFactory, transpiler: ITranspiler) -> None:
		"""インスタンスを生成

		Args:
			sources (ISourceLoader): ソースコードローダー @inject
			config (Config): コンフィグ @inject
			module_paths (ModulePaths): モジュールパスリスト @inject
			modules (Modules): モジュールリスト @inject
			module_meta_factory (ModuleMetaFactory): モジュールのメタ情報ファクトリー @inject
			transpiler (ITranspiler): トランスパイラー @inject
		"""
		self.sources = sources
		self.module_paths = module_paths
		self.modules = modules
		self.config = config
		self.module_meta_factory = module_meta_factory
		self.transpiler = transpiler

	def exec(self) -> None:
		"""トランスパイルの実行"""
		if self.config.profile:
			profiler('tottime')(self._exec)()
		else:
			self._exec()

	def _exec(self) -> None:
		"""トランスパイルの実行"""
		for module_path in self.module_paths:
			if self.config.force or self.can_transpile(module_path):
				content = self.transpiler.transpile(self.by_entrypoint(module_path))
				writer = Writer(self.output_filepath(module_path))
				writer.put(content)
				writer.flush()

	def try_load_meta_header(self, module_path: ModulePath) -> MetaHeader | None:
		"""トランスパイル済みのファイルからメタヘッダーの読み込みを試行

		Args:
			module_path (ModulePath): モジュールパス
		Returns:
			MetaHeader | None: メタヘッダー。ファイル・メタヘッダーが存在しない場合はNone
		"""
		filepath = self.output_filepath(module_path)
		if not self.sources.exists(filepath):
			return None

		return MetaHeader.try_from_content(self.sources.load(filepath))

	def output_filepath(self, module_path: ModulePath) -> str:
		"""トランスパイル後のファイルパスを生成

		Args:
			module_path (ModulePath): モジュールパス
		Returns:
			str: ファイルパス
		"""
		extension_map = self.config.output_language.split(':')
		extension = extension_map[1] if len(extension_map) == 2 else extension_map[0]
		filepath = module_path_to_filepath(module_path.path, f'.{extension}')
		output_dir = self._fetch_output_dir(filepath)
		return os.path.abspath(os.path.join(output_dir, filepath))

	def _fetch_output_dir(self, filepath: str) -> str:
		"""ファイルパスに応じた出力ディレクトリーを取得

		Args:
			filepath (str): ファイルパス
		Returns:
			str: 出力ディレクトリー
		"""
		_filepath = filepath.replace(os.sep, '/')
		fallback = self.config.output_dirs[-1]
		for dir_entry in self.config.output_dirs[:-1]:
			condition, output_dir = dir_entry.split(':')
			pattern = condition.replace('*', '.+')
			if re.fullmatch(pattern, _filepath):
				return output_dir

		return fallback

	def can_transpile(self, module_path: ModulePath) -> bool:
		"""トランスパイルを実行するか判定

		Args:
			module_path (ModulePath): モジュールパス
		Returns:
			bool: True = 実行
		"""
		old_meta = self.try_load_meta_header(module_path)
		if not old_meta:
			return True

		new_meta = MetaHeader(self.module_meta_factory(module_path.path), self.transpiler.meta)
		return new_meta != old_meta

	def by_entrypoint(self, module_path: ModulePath) -> Node:
		"""エントリーポイントのノードを取得

		Args:
			module_path (ModulePath): モジュールパス
		Returns:
			Node: ノード
		"""
		return self.modules.load(module_path.path).entrypoint


class Interactive:
	"""ランナー(対話モード)"""

	def __init__(self, locator: Locator) -> None:
		"""インスタンスを生成

		Args:
			locator (Locator): ロケーター
		"""
		# XXX リバインドより、定義側から変更する方法を検討
		di = as_a(DI, locator)
		di.rebind(SourceProvider, WrapSourceProvider)
		di.rebind(ModuleMetaFactory, make_dummy_module_meta_factory)
		self.source_provider = as_a(WrapSourceProvider, locator.resolve(SourceProvider))
		self.modules = locator.resolve(Modules)
		self.transpiler = locator.resolve(ITranspiler)

	def exec(self) -> None:
		"""対話モードの実行処理"""
		try:
			while True:
				print('===============')
				print('Python code here. Type `exit()` to quit:')

				lines: list[str] = []
				while True:
					line = readline()
					if not line:
						break

					lines.append(line)

				if len(lines) == 1 and lines[0] == 'exit()':
					break

				main_module = self.remake_module('\n'.join(lines))
				result = self.transpiler.transpile(main_module.entrypoint)

				print('===============')
				print('Result:')
				print('---------------')
				print(result)
		except KeyboardInterrupt:
			pass
		finally:
			print('Quit')

	def remake_module(self, source_code: str) -> Module:
		"""モジュールを再生成

		Args:
			source_code (str): ソースコード
		Returns:
			Note: エントリーポイント
		"""
		self.source_provider.source_code = source_code
		self.modules.unload(self.source_provider.main_module_path)
		return self.modules.load(self.source_provider.main_module_path)


if __name__ == '__main__':
	try:
		App(TranspileApp.definitions()).run(TranspileApp.run)
	except Exception as e:
		print(''.join(stacktrace(e)))
