import os
import sys
from typing import TypedDict, cast

import yaml

from rogw.tranp.app.app import App
from rogw.tranp.data.meta.header import MetaHeader
from rogw.tranp.data.meta.types import ModuleMetaFactory
from rogw.tranp.i18n.i18n import TranslationMapping
from rogw.tranp.implements.cpp.providers.semantics import cpp_plugin_provider
from rogw.tranp.implements.cpp.transpiler.py2cpp import Py2Cpp
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.io.writer import Writer
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.di import ModuleDefinitions
from rogw.tranp.lang.error import stacktrace
from rogw.tranp.lang.module import fullyname
from rogw.tranp.lang.profile import profiler
from rogw.tranp.module.includer import include_module_paths
from rogw.tranp.module.modules import Modules
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.syntax.ast.parser import ParserSetting
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.transpiler.types import ITranspiler, TranspilerOptions
from rogw.tranp.view.render import Renderer

ArgsDict = TypedDict('ArgsDict', {
	'config': str,
	'force': bool,
	'verbose': bool,
	'profile': str,
})
ConfigDict = TypedDict('ConfigDict', {
	'grammar': str,
	'template_dir': str,
	'trans_mapping': str,
	'input_glob': str,
	'exclude_patterns': list[str],
	'output_dir': str,
	'output_language': str,
	'force': bool,
	'verbose': bool,
	'profile': str,
})


class Config:
	"""コンフィグ"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		args = self.__parse_argv(sys.argv[1:])
		config = self.__load_config(args['config'])
		self.grammar = config['grammar']
		self.template_dir = config['template_dir']
		self.trans_mapping = config['trans_mapping']
		self.input_glob = config['input_glob']
		self.exclude_patterns = config['exclude_patterns']
		self.output_dir = config['output_dir']
		self.output_language = config['output_language']
		self.force = config.get('force', args['force'])
		self.verbose = config.get('verbose', args['verbose'])
		self.profile = config.get('profile', args['profile'])

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
			'profile': '',
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
				args['profile'] = argv.pop(0)

		return args


class TranspileApp:
	"""トランスパイルアプリケーション"""

	@classmethod
	@injectable
	def make_renderer(cls, config: Config) -> Renderer:
		"""テンプレートレンダーを生成

		Args:
			config (Config): コンフィグ @inject
		Returns:
			Renderer: テンプレートレンダー
		"""
		return Renderer(config.template_dir)

	@classmethod
	@injectable
	def make_options(cls, config: Config) -> TranspilerOptions:
		"""トランスパイルオプションを生成

		Args:
			config (Config): コンフィグ @inject
		Returns:
			TranspilerOptions: トランスパイルオプション
		"""
		return TranspilerOptions(verbose=config.verbose)

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
	def make_translation_mapping(cls, loader: IFileLoader, config: Config) -> TranslationMapping:
		"""翻訳マッピングデータを生成

		Args:
			loader (IFileLoader): ファイルローダー @inject
			config (Config): コンフィグ @inject
		Returns:
			TranslationMapping: 翻訳マッピングデータ
		"""
		mapping = cast(dict[str, str], yaml.safe_load(loader.load(config.trans_mapping)))
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
		return include_module_paths(config.input_glob, config.exclude_patterns)

	@classmethod
	def definitions(cls) -> ModuleDefinitions:
		"""モジュール定義を生成

		Returns:
			ModuleDefinitions: モジュール定義
		"""
		return {
			fullyname(Config): Config,
			fullyname(ITranspiler): Py2Cpp,
			fullyname(ModulePaths): cls.make_module_paths,
			fullyname(ParserSetting): cls.make_parser_setting,
			fullyname(PluginProvider): cpp_plugin_provider,  # FIXME C++固定
			fullyname(Renderer): cls.make_renderer,
			fullyname(TranslationMapping): cls.make_translation_mapping,
			fullyname(TranspilerOptions): cls.make_options,
		}

	@classmethod
	@injectable
	def run(cls, loader: IFileLoader, config: Config, module_paths: ModulePaths, modules: Modules, module_meta_factory: ModuleMetaFactory, transpiler: ITranspiler) -> None:
		"""アプリケーションを実行

		Args:
			loader (IFilerLoader): ファイルローダー @inject
			config (Config): コンフィグ @inject
			module_paths (ModulePaths): モジュールパスリスト @inject
			modules (Modules): モジュールリスト @inject
			module_meta_factory (ModuleMetaFactory): モジュールのメタ情報ファクトリー @inject
			transpiler (ITranspiler): トランスパイラー @inject
		"""
		app = cls(loader, config, module_paths, modules, module_meta_factory, transpiler)
		if config.profile in ['tottime', 'cumtime']:
			profiler(config.profile)(app.exec)()
		else:
			app.exec()

	def __init__(self, loader: IFileLoader, config: Config, module_paths: ModulePaths, modules: Modules, module_meta_factory: ModuleMetaFactory, transpiler: ITranspiler) -> None:
		"""インスタンスを生成 Args: @see run"""
		self.loader = loader
		self.module_paths = module_paths
		self.modules = modules
		self.config = config
		self.module_meta_factory = module_meta_factory
		self.transpiler = transpiler

	def try_load_meta_header(self, module_path: ModulePath) -> MetaHeader | None:
		"""トランスパイル済みのファイルからメタヘッダーの読み込みを試行

		Args:
			module_path (ModulePath): モジュールパス
		Returns:
			MetaHeader | None: メタヘッダー。ファイル・メタヘッダーが存在しない場合はNone
		"""
		filepath = self.output_filepath(module_path)
		if not self.loader.exists(filepath):
			return None

		return MetaHeader.try_from_content(self.loader.load(filepath))

	def output_filepath(self, module_path: ModulePath) -> str:
		"""トランスパイル後のファイルパスを生成

		Args:
			module_path (ModulePath): モジュールパス
		Returns:
			str: ファイルパス
		"""
		basepath = module_path.path.replace('.', '/')
		filepath = f'{basepath}.{self.config.output_language}'
		return os.path.abspath(os.path.join(self.config.output_dir, filepath))

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

	def exec(self) -> None:
		"""トランスパイルの実行"""
		for module_path in self.module_paths:
			if self.config.force or self.can_transpile(module_path):
				content = self.transpiler.transpile(self.by_entrypoint(module_path))
				writer = Writer(self.output_filepath(module_path))
				writer.put(content)
				writer.flush()


if __name__ == '__main__':
	try:
		App(TranspileApp.definitions()).run(TranspileApp.run)
	except Exception as e:
		print(''.join(stacktrace(e)))
