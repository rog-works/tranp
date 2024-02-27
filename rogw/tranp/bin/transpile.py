import os
import sys

from rogw.tranp.analyze.plugin import PluginProvider
from rogw.tranp.app.app import App
from rogw.tranp.ast.parser import ParserSetting
import rogw.tranp.compatible.python.embed as __alias__
from rogw.tranp.implements.cpp.providers.analyze import cpp_plugin_provider
from rogw.tranp.lang.error import stacktrace
from rogw.tranp.lang.module import fullyname
from rogw.tranp.module.types import ModulePath
from rogw.tranp.node.node import Node
from rogw.tranp.translator.option import TranslatorOptions
from rogw.tranp.translator.py2cpp import Py2Cpp
from rogw.tranp.view.render import Renderer, Writer
from rogw.tranp.lang.profile import profiler


class Args:
	def __init__(self) -> None:
		args = self.__parse_argv(sys.argv[1:])
		self.grammar = args['grammar']
		self.source = args['source']
		self.template_dir = args['template_dir']
		self.verbose = args['verbose'] == 'on'
		self.profile = args['profile']

	def __parse_argv(self, argv: list[str]) -> dict[str, str]:
		args = {
			'grammar': 'data/grammar.lark',
			'source': 'example/example.py',
			'template_dir': 'example/template',
			'verbose': 'off',
			'profile': 'off',
		}
		while argv:
			arg = argv.pop(0)
			if arg == '-g':
				args['grammar'] = argv.pop(0)
			elif arg == '-s':
				args['source'] = argv.pop(0)
			elif arg == '-t':
				args['template_dir'] = argv.pop(0)
			elif arg == '-v':
				args['verbose'] = 'on'
			elif arg == '-p':
				args['profile'] = argv.pop(0)

		return args


def make_writer(args: Args) -> Writer:
	basepath, _ = os.path.splitext(args.source)
	output = f'{basepath}.h'
	return Writer(output)


def make_renderer(args: Args) -> Renderer:
	return Renderer(args.template_dir)


def make_options(args: Args) -> TranslatorOptions:
	return TranslatorOptions(verbose=args.verbose)


def make_parser_setting(args: Args) -> ParserSetting:
	return ParserSetting(grammar=args.grammar)


def make_module_path(args: Args) -> ModulePath:
	basepath, _ = os.path.splitext(args.source)
	module_path = basepath.replace('/', '.')
	return ModulePath('__main__', module_path)


def task(translator: Py2Cpp, root: Node, writer: Writer, args: Args) -> None:
	def run() -> None:
		try:
			writer.put(translator.translate(root))
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
		fullyname(Writer): make_writer,
		fullyname(Renderer): make_renderer,
		fullyname(TranslatorOptions): make_options,
		fullyname(Py2Cpp): Py2Cpp,
		fullyname(ParserSetting): make_parser_setting,
		fullyname(ModulePath): make_module_path,
		fullyname(PluginProvider): cpp_plugin_provider,
	}
	App(definitions).run(task)
