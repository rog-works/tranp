import os
from typing import Callable, cast

from lark import Lark, Tree
from lark.indenter import PythonIndenter

from py2cpp.ast.entry import Entry
from py2cpp.ast.parser import ParserSettings, SyntaxParser
from py2cpp.lang.annotation import implements
from py2cpp.lang.io import FileLoader
from py2cpp.lang.module import load_module
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
		if Cache.exists('./.cache/py2cpp/parser.cache'):
			return Cache.load('./.cache/py2cpp/parser.cache')

		grammar = self.__loader(self.__settings.grammar)
		lark = Lark(grammar, start=self.__settings.start, postlex=PythonIndenter(), parser=self.__settings.algorihtem)

		Cache.save('./.cache/py2cpp/parser.cache', lark)
		return lark

	def __load_source(self, module_path: str) -> str:
		filepath = module_path.replace('.', '/')
		source_path = f'{filepath}.py'
		return self.__loader(source_path)


class Cache:
	@classmethod
	def exists(cls, filepath: str) -> bool:
		return os.path.exists(filepath)

	@classmethod
	def save(cls, filepath: str, lark: Lark) -> None:
		with open(filepath, mode='wb') as f:
			lark.save(f)

	@classmethod
	def load(cls, filepath: str) -> Lark:
		with open(filepath, mode='rb') as f:
			return Lark.load(f)

	# @classmethod
	# def save_tree(cls, filepath: str, tree: Tree) -> None:
	# 	pretty = '\n# '.join(tree.pretty().split('\n'))
	# 	lines = [
	# 		'from lark import Tree, Token',
	# 		'def tree() -> Tree:',
	# 		f'	return {str(tree)}',
	# 		'# ==========',
	# 		f'# {pretty}',
	# 	]
	# 	with open(filepath, mode='wb') as f:
	# 		f.write(('\n'.join(lines)).encode('utf-8'))

	# @classmethod
	# def load_tree(cls, filepath: str) -> Tree:
	# 	cwd = os.getcwd()
	# 	dirpath, filename = os.path.dirname(filepath), os.path.basename(filepath)
	# 	os.chdir(dirpath)
	# 	module_path = filename.split('.')
	# 	tree = cast(Callable[[], Tree], load_module(module_path, 'tree'))
	# 	os.chdir(cwd)
	# 	return tree()
