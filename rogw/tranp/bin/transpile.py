import os
import sys

from rogw.tranp.app.app import App
from rogw.tranp.i18n.i18n import TranslationMapping
from rogw.tranp.implements.cpp.providers.i18n import translation_mapping
from rogw.tranp.implements.cpp.providers.semantics import cpp_plugin_provider
from rogw.tranp.lang.error import stacktrace
from rogw.tranp.lang.implementation import injectable
from rogw.tranp.lang.module import fullyname
from rogw.tranp.lang.profile import profiler
from rogw.tranp.module.modules import Modules
from rogw.tranp.module.types import ModulePath, ModulePaths
from rogw.tranp.semantics.plugin import PluginProvider
from rogw.tranp.syntax.ast.parser import ParserSetting
from rogw.tranp.syntax.node.node import Node
from rogw.tranp.translator.option import TranslatorOptions
from rogw.tranp.translator.py2cpp import Py2Cpp
from rogw.tranp.view.render import Renderer, Writer


class Args:
	def __init__(self) -> None:
		args = self.__parse_argv(sys.argv[1:])
		self.grammar = args['grammar']
		self.input = args['input']
		self.output = args['output']
		self.template_dir = args['template_dir']
		self.verbose = args['verbose'] == 'on'
		self.profile = args['profile']

	def __parse_argv(self, argv: list[str]) -> dict[str, str]:
		args = {
			'grammar': 'data/grammar.lark',
			'input': 'example/example.py',
			'output': '',
			'template_dir': 'example/template',
			'verbose': 'off',
			'profile': 'off',
		}
		while argv:
			arg = argv.pop(0)
			if arg == '-g':
				args['grammar'] = argv.pop(0)
			elif arg == '-i':
				args['input'] = argv.pop(0)
			elif arg == '-o':
				args['output'] = argv.pop(0)
			elif arg == '-t':
				args['template_dir'] = argv.pop(0)
			elif arg == '-v':
				args['verbose'] = 'on'
			elif arg == '-p':
				args['profile'] = argv.pop(0)

		return args


def make_writer(args: Args) -> Writer:
	basepath, _ = os.path.splitext(args.input)
	output = args.output if args.output else f'{basepath}.h'
	return Writer(output)


def make_renderer(args: Args) -> Renderer:
	return Renderer(args.template_dir)


def make_options(args: Args) -> TranslatorOptions:
	return TranslatorOptions(verbose=args.verbose)


def make_parser_setting(args: Args) -> ParserSetting:
	return ParserSetting(grammar=args.grammar)


def make_module_paths(args: Args) -> list[ModulePath]:
	basepath, extention = os.path.splitext(args.input)
	return [ModulePath(basepath.replace('/', '.'), language=extention[1:])]


def fetch_main_entrypoint(modules: Modules, module_paths: ModulePaths) -> Node:
	"""Note: FIXME 複数の出力対象に対応"""
	return modules.load(module_paths[0].path).entrypoint


@injectable
def task(translator: Py2Cpp, modules: Modules, module_paths: ModulePaths, writer: Writer, args: Args) -> None:
	def run() -> None:
		try:
			entrypoint = fetch_main_entrypoint(modules, module_paths)
			writer.put(translator.translate(entrypoint))
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
		fullyname(ModulePaths): make_module_paths,
		fullyname(ParserSetting): make_parser_setting,
		fullyname(PluginProvider): cpp_plugin_provider,
		fullyname(Py2Cpp): Py2Cpp,
		fullyname(Renderer): make_renderer,
		fullyname(TranslationMapping): translation_mapping,
		fullyname(TranslatorOptions): make_options,
		fullyname(Writer): make_writer,
	}
	App(definitions).run(task)
