import os
import json
from typing import IO, cast

from lark import Lark, Tree
from lark.indenter import PythonIndenter

from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import ParserSetting, SyntaxParser
from py2cpp.lang.annotation import implements
from py2cpp.lang.cache import CacheProvider, Lifecycle
from py2cpp.lang.io import FileLoader
from py2cpp.tp_lark.entry import EntryOfLark, Serialization


class LarkLifecycle(Lifecycle[Lark]):
	def __init__(self, loader: FileLoader, settings: ParserSetting) -> None:
		self.__loader = loader
		self.__settings = settings

	@implements
	def instantiate(self) -> Lark:
		return Lark(
			self.__loader(self.__settings.grammar),
			start=self.__settings.start,
			parser=self.__settings.algorithem,
			postlex=PythonIndenter()
		)

	@implements
	def context(self) -> dict[str, str]:
		return {
			'mtime': str(os.path.getmtime(self.__settings.grammar)),
			'grammar': self.__settings.grammar,
			'start': self.__settings.start,
			'algorithem': self.__settings.algorithem,
		}

	@implements
	def save(self, instance: Lark, f: IO) -> None:
		instance.save(f)

	@implements
	def load(self, f: IO) -> Lark:
		return Lark.load(f)


class EntryLifecycle(Lifecycle[Entry]):
	def __init__(self, loader: FileLoader, parser: Lark, module_path: str) -> None:
		self.__loader = loader
		self.__parser = parser
		self.__source_path = self.to_source_path(module_path)

	def to_source_path(self, module_path: str) -> str:
		filepath = module_path.replace('.', '/')
		return f'{filepath}.py'

	@implements
	def instantiate(self) -> Entry:
		tree = self.__parser.parse(self.load_source())
		return EntryOfLark(tree)

	def load_source(self) -> str:
		return self.__loader(self.__source_path)

	@implements
	def context(self) -> dict[str, str]:
		return {'mtime': str(os.path.getmtime(self.__source_path))}

	@implements
	def save(self, instance: Entry, f: IO) -> None:
		# XXX JSONと比べてかなり遅いため一旦廃止
		# import yaml
		# data = Serialization.dumps(cast(Tree, instance.source))
		# yaml.safe_dump(data, f, encoding='utf-8', sort_keys=False)

		data = Serialization.dumps(cast(Tree, instance.source))
		f.write(json.dumps(data).encode('utf-8'))

	@implements
	def load(self, f: IO) -> Entry:
		# XXX JSONと比べてかなり遅いため一旦廃止
		# import yaml
		# data = cast(dict[str, Any], yaml.safe_load(f))

		data = json.load(f)
		tree = cast(Tree, Serialization.loads(data))
		return EntryOfLark(tree)


class SyntaxParserOfLark(SyntaxParser):
	def __init__(self, loader: FileLoader, settings: ParserSetting, cache: CacheProvider) -> None:
		self.__loader = loader
		self.__cache = cache
		self.__parser = self.__cache.provide(LarkLifecycle(loader, settings))

	@implements
	def parse(self, module_path: str) -> Entry:
		parser = self.__load_parser()
		return self.__load_entry(parser, module_path)

	def __load_parser(self) -> Lark:
		return self.__parser.get('parser.cache')

	def __load_entry(self, parser: Lark, module_path: str) -> Entry:
		basepath = module_path.replace('.', '/')
		entry = self.__cache.provide(EntryLifecycle(self.__loader, parser, module_path))
		# XXX JSONと比べてかなり遅いため一旦廃止
		# return entry.get(f'{basepath}.yml')
		return entry.get(f'{basepath}.json')
