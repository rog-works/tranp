import os
from typing import IO

from lark import Lark
from lark.indenter import PythonIndenter

from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import ParserSettings, SyntaxParser
from py2cpp.lang.annotation import implements
from py2cpp.lang.io import FileLoader
from py2cpp.lang.proxy import CachedProxy
from py2cpp.tp_lark.entry import EntryOfLark


class LarkLifecycle:
	def __init__(self, loader: FileLoader, settings: ParserSettings) -> None:
		self.__loader = loader
		self.__settings = settings

	def instantiate(self) -> Lark:
		return Lark(
			self.__loader(self.__settings.grammar),
			start=self.__settings.start,
			parser=self.__settings.algorithem,
			postlex=PythonIndenter()
		)

	def context(self) -> dict[str, str]:
		return {
			'mtime': str(os.path.getmtime(self.__settings.grammar)),
			'grammar': self.__settings.grammar,
			'start': self.__settings.start,
			'algorithem': self.__settings.algorithem,
		}

	def save(self, instance: Lark, f: IO) -> None:
		instance.save(f)

	def load(self, f: IO) -> Lark:
		return Lark.load(f)


class SyntaxParserOfLark(SyntaxParser):
	def __init__(self, loader: FileLoader, settings: ParserSettings) -> None:
		self.__loader = loader
		self.__parser = CachedProxy(LarkLifecycle(loader, settings))

	@implements
	def parse(self, module_path: str) -> Entry:
		parser = self.__load_parser()
		source = self.__load_source(module_path)
		return EntryOfLark(parser.parse(source))

	def __load_parser(self) -> Lark:
		return self.__parser.get('./.cache/py2cpp/parser.cache')

	def __load_source(self, module_path: str) -> str:
		filepath = module_path.replace('.', '/')
		source_path = f'{filepath}.py'
		return self.__loader(source_path)
