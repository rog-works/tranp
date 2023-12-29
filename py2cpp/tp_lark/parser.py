from lark import Lark
from lark.indenter import PythonIndenter

from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import ParserSettings, SyntaxParser
from py2cpp.lang.annotation import implements
from py2cpp.lang.io import FileLoader
from py2cpp.tp_lark.entry import EntryOfLark


class SyntaxParserOfLark(SyntaxParser):
	def __init__(self, loader: FileLoader, settings: ParserSettings) -> None:
		self.__loader = loader
		self.__settings = settings

	@implements
	def parse(self, module_path: str) -> Entry:
		parser = self.__load_parser()
		source = self.__load_source(module_path)
		return EntryOfLark(parser.parse(source))

	def __load_parser(self) -> Lark:
		grammar = self.__loader(self.__settings.grammar)
		return Lark(grammar, start=self.__settings.start, postlex=PythonIndenter(), parser=self.__settings.algorihtem)

	def __load_source(self, module_path: str) -> str:
		filepath = module_path.replace('.', '/')
		source_path = f'{filepath}.py'
		return self.__loader(source_path)
