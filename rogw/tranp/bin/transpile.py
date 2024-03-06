import glob
import os
import re
import sys
from typing import TypedDict

from rogw.tranp.app.app import App
from rogw.tranp.errors import LogicError
from rogw.tranp.i18n.i18n import TranslationMapping
from rogw.tranp.implements.cpp.providers.i18n import translation_mapping_cpp
from rogw.tranp.implements.cpp.providers.semantics import cpp_plugin_provider
from rogw.tranp.implements.cpp.translator.py2cpp import Py2Cpp
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.io.writer import Writer
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.error import stacktrace
from rogw.tranp.lang.module import fullyname
from rogw.tranp.lang.profile import profiler
from rogw.tranp.meta.header import MetaHeader
from rogw.tranp.meta.types import ModuleMeta, ModuleMetaInjector
from rogw.tranp.module.modules import Modules
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.syntax.ast.dsn import DSN
from rogw.tranp.syntax.ast.parser import ParserSetting
from rogw.tranp.translator.types import ITranslator, TranslatorOptions
from rogw.tranp.view.render import Renderer

ArgsDict = TypedDict('ArgsDict', {'grammar': str, 'template_dir': str, 'input_dir': str, 'output_dir': str, 'output_lang': str, 'excludes': list[str], 'force': bool, 'verbose': bool, 'profile': str})


class Args:
	def __init__(self) -> None:
		args = self.__parse_argv(sys.argv[1:])
		self.grammar = args['grammar']
		self.template_dir = args['template_dir']
		self.input_dir = args['input_dir']
		self.output_dir = args['output_dir']
		self.output_lang = args['output_lang']
		self.excludes = args['excludes']
		self.force = args['force']
		self.verbose = args['verbose']
		self.profile = args['profile']

	def __parse_argv(self, argv: list[str]) -> ArgsDict:
		args: ArgsDict = {
			'grammar': 'data/grammar.lark',
			'input_dir': 'example/**/*.py',
			'output_dir': './',
			'output_lang': 'h',
			'excludes': ['example/FW/*'],
			'template_dir': 'example/template',
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
				args['input_dir'] = argv.pop(0)
			elif arg == '-o':
				args['output_dir'] = argv.pop(0)
			elif arg == '-l':
				args['output_lang'] = argv.pop(0)
			elif arg == '-e':
				args['excludes'] = argv.pop(0).split(';')
			elif arg == '-f':
				args['force'] = True
			elif arg == '-v':
				args['verbose'] = argv.pop(0) == 'on'
			elif arg == '-p':
				args['profile'] = argv.pop(0)

		return args


@injectable
def make_renderer(args: Args) -> Renderer:
	return Renderer(args.template_dir)


@injectable
def make_module_mata_injector(module_paths: ModulePaths, loader: IFileLoader) -> ModuleMetaInjector:
	def injector(module_path: str) -> ModuleMeta:
		index = [module_path.path for module_path in module_paths].index(module_path)
		target_module_path = module_paths[index]
		basepath = target_module_path.path.replace('.', '/')
		filepath = DSN.join(basepath, target_module_path.language)
		return {'hash': loader.hash(filepath), 'path': module_path}

	return injector


def load_meta_header_json(module_path: ModulePath, loader: IFileLoader) -> str | None:
	basepath = module_path.path.replace('.', '/')
	filepath = DSN.join(basepath, module_path.language)
	content = loader.load(filepath)
	header_begin = content.find(MetaHeader.Tag)
	if header_begin == -1:
		return None

	header_end = content.find('\n', header_begin)
	return content[header_begin:header_end]


@injectable
def make_options(args: Args) -> TranslatorOptions:
	return TranslatorOptions(verbose=args.verbose)


@injectable
def make_parser_setting(args: Args) -> ParserSetting:
	return ParserSetting(grammar=args.grammar)


@injectable
def make_module_paths(args: Args) -> ModulePaths:
	candidate_filepaths = glob.glob(args.input_dir, recursive=True)
	exclude_exps = [re.compile(rf'{exclude.replace("*", '.*')}') for exclude in args.excludes]
	module_paths = ModulePaths()
	for filepath in candidate_filepaths:
		excluded = len([True for exclude_exp in exclude_exps if exclude_exp.fullmatch(filepath)]) > 0
		if not excluded:
			basepath, extention = os.path.splitext(filepath)
			module_paths.append(ModulePath(basepath.replace('/', '.'), language=extention[1:]))

	if len(module_paths) == 0:
		raise LogicError(f'No target found. input_dir: {args.input_dir}, excludes: {args.excludes}')

	return module_paths


def output_filepath(module_path: ModulePath, args: Args) -> str:
	basepath = module_path.path.replace('.', '/')
	filepath = f'{basepath}.{args.output_lang}'
	return os.path.abspath(os.path.join(args.output_dir, filepath))


@injectable
def task(translator: ITranslator, modules: Modules, module_paths: ModulePaths, args: Args, loader: IFileLoader) -> None:
	def run() -> None:
		try:
			module_meta_injector = make_module_mata_injector(module_paths, loader)
			for module_path in module_paths:
				header_json = load_meta_header_json(module_path, loader)
				if header_json:
					new_meta = MetaHeader(module_meta_injector(module_path.path), translator.meta)
					old_meta = MetaHeader.from_json(header_json)
					if not args.force and not new_meta == old_meta:
						continue

				content = translator.translate(modules.load(module_path.path))
				writer = Writer(output_filepath(module_path, args))
				writer.put(content)
				writer.flush()
		except Exception as e:
			print(''.join(stacktrace(e)))

	if args.profile in ['tottime', 'cumtime']:
		profiler(args.profile)(run)()
	else:
		run()


if __name__ == '__main__':
	definitions = {
		fullyname(Args): Args,
		fullyname(ModuleMetaInjector): make_module_mata_injector,
		fullyname(ModulePaths): make_module_paths,
		fullyname(ParserSetting): make_parser_setting,
		fullyname(PluginProvider): cpp_plugin_provider,
		fullyname(ITranslator): Py2Cpp,
		fullyname(Renderer): make_renderer,
		fullyname(TranslationMapping): translation_mapping_cpp,
		fullyname(TranslatorOptions): make_options,
	}
	App(definitions).run(task)
