from lark import Tree, Token

from py2cpp.tp_lark.travarsal import pluck_entry


class AstBuilder:
	def __init__(self, root_tag: str) -> None:
		self.__root = Tree(root_tag, [])
		self.__path = root_tag
		self.__prev = self.__root


	def __calc_path(self, path: str) -> str:
		if path == '$':
			return self.__root.data
		elif path.startswith('$.'):
			return f'{self.__root.data}{".".join(path.split(".")[1:])}'
		elif path.startswith('.'):
			return f'{self.__path}.{path}'

		raise ValueError()


	def tree(self, path: str, tag: str) -> 'AstBuilder':
		entry = self.__prev
		base = self.__path
		if path == '$' or path.startswith('$.') or path.startswith('.'):
			base = self.__calc_path(path)
			entry = pluck_entry(self.__root, base)

		if entry is Tree:
			tree = Tree(tag, [])
			entry.children.append()
			self.__path = f'{base}.{tag}'
			self.__prev = tree
			return self

		raise ValueError()


	def token(self, path: str, tag: str) -> 'AstBuilder':
		entry = self.__prev
		base = self.__path
		if path == '$' or path.startswith('$.') or path.startswith('.'):
			base = self.__calc_path(path)
			entry = pluck_entry(self.__root, base)

		if entry is Tree:
			entry.children.append(Token(tag, ''))
			self.__path = base
			self.__prev = entry
			return self

		raise ValueError()


	def result(self) -> Tree:
		return self.__root
