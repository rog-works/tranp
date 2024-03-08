import os
import sys
from typing import TypedDict

from rogw.tranp.app.app import App
from rogw.tranp.data.meta.header import MetaHeader
from rogw.tranp.data.meta.types import ModuleMetaFactory
from rogw.tranp.i18n.i18n import TranslationMapping
from rogw.tranp.implements.cpp.providers.i18n import translation_mapping_cpp
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

ArgsDict = TypedDict('ArgsDict', {'grammar': str, 'template_dir': str, 'input_glob': str, 'exclude_patterns': list[str], 'output_dir': str, 'output_language': str, 'force': bool, 'verbose': bool, 'profile': str})


class Args:
	"""コマンド引数"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		args = self.__parse_argv(sys.argv[1:])
		self.grammar = args['grammar']
		self.template_dir = args['template_dir']
		self.input_glob = args['input_glob']
		self.exclude_patterns = args['exclude_patterns']
		self.output_dir = args['output_dir']
		self.output_language = args['output_language']
		self.force = args['force']
		self.verbose = args['verbose']
		self.profile = args['profile']

	def __parse_argv(self, argv: list[str]) -> ArgsDict:
		"""コマンド引数をパース

		Args:
			argv (list[str]): コマンド引数リスト
		Returns:
			ArgsDict: パースしたコマンド引数
		"""
		args: ArgsDict = {
			'grammar': 'data/grammar.lark',
			'input_glob': 'example/**/*.py',
			'output_dir': './',
			'output_language': 'h',
			'exclude_patterns': ['example/FW/*'],
			'template_dir': 'data/cpp/template',
			'force': False,
			'verbose': False,
			'profile': 'none',
		}
		while argv:
			arg = argv.pop(0)
			if arg == '-g':
				args['grammar'] = argv.pop(0)
			elif arg == '-t':
				args['template_dir'] = argv.pop(0)
			elif arg == '-i':
				args['input_glob'] = argv.pop(0)
			elif arg == '-o':
				args['output_dir'] = argv.pop(0)
			elif arg == '-l':
				args['output_language'] = argv.pop(0)
			elif arg == '-e':
				args['exclude_patterns'] = argv.pop(0).split(';')
			elif arg == '-f':
				args['force'] = True
			elif arg == '-v':
				args['verbose'] = argv.pop(0) == 'on'
			elif arg == '-p':
				args['profile'] = argv.pop(0)

		return args


class TranspileApp:
	"""トランスパイルアプリケーション"""

	@classmethod
	@injectable
	def make_renderer(cls, args: Args) -> Renderer:
		"""テンプレートレンダーを生成

		Args:
			args (Args): コマンド引数 @inject
		Returns:
			Renderer: テンプレートレンダー
		"""
		return Renderer(args.template_dir)

	@classmethod
	@injectable
	def make_options(cls, args: Args) -> TranspilerOptions:
		"""トランスパイルオプションを生成

		Args:
			args (Args): コマンド引数 @inject
		Returns:
			TranspilerOptions: トランスパイルオプション
		"""
		return TranspilerOptions(verbose=args.verbose)

	@classmethod
	@injectable
	def make_parser_setting(cls, args: Args) -> ParserSetting:
		"""シンタックスパーサー設定データを生成

		Args:
			args (Args): コマンド引数 @inject
		Returns:
			ParserSetting: シンタックスパーサー設定データ
		"""
		return ParserSetting(grammar=args.grammar)

	@classmethod
	@injectable
	def make_module_paths(cls, args: Args) -> ModulePaths:
		"""モジュールパスリストを生成

		Args:
			args (Args): コマンド引数 @inject
		Returns:
			ModulePaths: モジュールパスリスト
		"""
		return include_module_paths(args.input_glob, args.exclude_patterns)

	@classmethod
	def definitions(cls) -> ModuleDefinitions:
		"""モジュール定義を生成

		Returns:
			ModuleDefinitions: モジュール定義
		"""
		return {
			fullyname(Args): Args,
			fullyname(ITranspiler): Py2Cpp,
			fullyname(ModulePaths): cls.make_module_paths,
			fullyname(ParserSetting): cls.make_parser_setting,
			fullyname(PluginProvider): cpp_plugin_provider,  # FIXME C++固定
			fullyname(Renderer): cls.make_renderer,
			fullyname(TranslationMapping): translation_mapping_cpp,  # FIXME C++固定
			fullyname(TranspilerOptions): cls.make_options,
		}

	@classmethod
	@injectable
	def run(cls, loader: IFileLoader, args: Args, module_paths: ModulePaths, modules: Modules, module_meta_factory: ModuleMetaFactory, transpiler: ITranspiler) -> None:
		"""アプリケーションを実行

		Args:
			loader (IFilerLoader): ファイルローダー @inject
			args (Args): コマンド引数 @inject
			module_paths (ModulePaths): モジュールパスリスト @inject
			modules (Modules): モジュールリスト @inject
			module_meta_factory (ModuleMetaFactory): モジュールのメタ情報ファクトリー @inject
			transpiler (ITranspiler): トランスパイラー @inject
		"""
		app = cls(loader, args, module_paths, modules, module_meta_factory, transpiler)
		if args.profile in ['tottime', 'cumtime']:
			profiler(args.profile)(app.exec)()
		else:
			app.exec()

	def __init__(self, loader: IFileLoader, args: Args, module_paths: ModulePaths, modules: Modules, module_meta_factory: ModuleMetaFactory, transpiler: ITranspiler) -> None:
		"""インスタンスを生成 Args: @see run"""
		self.loader = loader
		self.module_paths = module_paths
		self.modules = modules
		self.args = args
		self.module_meta_factory = module_meta_factory
		self.transpiler = transpiler

	def try_load_meta_header(self, module_path: ModulePath) -> MetaHeader | None:
		"""トランスパイル済みのファイルからメタヘッダーの読み込みを試行

		Args:
			module_path (ModulePath)
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
			module_path (ModulePath)
		Returns:
			str: ファイルパス
		"""
		basepath = module_path.path.replace('.', '/')
		filepath = f'{basepath}.{self.args.output_language}'
		return os.path.abspath(os.path.join(self.args.output_dir, filepath))

	def can_transpile(self, module_path: ModulePath) -> bool:
		"""トランスパイルを実行するか判定

		Args:
			module_path (ModulePath)
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
			module_path (ModulePath)
		Returns:
			Node: ノード
		"""
		return self.modules.load(module_path.path).entrypoint

	def exec(self) -> None:
		"""トランスパイルの実行"""
		for module_path in self.module_paths:
			if self.args.force or self.can_transpile(module_path):
				content = self.transpiler.transpile(self.by_entrypoint(module_path))
				writer = Writer(self.output_filepath(module_path))
				writer.put(content)
				writer.flush()


if __name__ == '__main__':
	try:
		App(TranspileApp.definitions()).run(TranspileApp.run)
	except Exception as e:
		print(''.join(stacktrace(e)))
