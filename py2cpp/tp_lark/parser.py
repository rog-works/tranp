import os
from typing import Any, IO, cast

from lark import Lark, Tree
from lark.indenter import PythonIndenter
import yaml

from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import ParserSettings, SyntaxParser
from py2cpp.lang.annotation import implements
from py2cpp.lang.io import FileLoader
from py2cpp.lang.proxy import CachedProxy
from py2cpp.tp_lark.entry import EntryOfLark, Serialization


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


class EntryLifecycle:
	def __init__(self, loader: FileLoader, parser: Lark, module_path: str) -> None:
		self.__loader = loader
		self.__parser = parser
		self.__source_path = self.to_source_path(module_path)

	def to_source_path(self, module_path: str) -> str:
		filepath = module_path.replace('.', '/')
		return f'{filepath}.py'

	def instantiate(self) -> EntryOfLark:
		tree = self.__parser.parse(self.load_source())
		return EntryOfLark(tree)

	def load_source(self) -> str:
		return self.__loader(self.__source_path)

	def context(self) -> dict[str, str]:
		return {'mtime': str(os.path.getmtime(self.__source_path))}

	def save(self, instance: EntryOfLark, f: IO) -> None:
		data = Serialization.dumps(cast(Tree, instance.source))
		yaml.safe_dump(data, f, encoding='utf-8', sort_keys=False)

	def load(self, f: IO) -> EntryOfLark:
		data = cast(dict[str, Any], yaml.safe_load(f))
		tree = cast(Tree, Serialization.loads(data))
		return EntryOfLark(tree)


class SyntaxParserOfLark(SyntaxParser):
	def __init__(self, loader: FileLoader, settings: ParserSettings) -> None:
		self.__loader = loader
		self.__parser = CachedProxy(LarkLifecycle(loader, settings))

	@implements
	def parse(self, module_path: str) -> Entry:
		parser = self.__load_parser()
		return self.__load_entry(parser, module_path)

	def __load_parser(self) -> Lark:
		return self.__parser.get('./.cache/py2cpp/parser.cache')

	def __load_entry(self, parser: Lark, module_path: str) -> Entry:
		basepath = module_path.replace('.', '/')
		entry = CachedProxy(EntryLifecycle(self.__loader, parser, module_path))
		return entry.get(f'./.cache/py2cpp/{basepath}.yml')
