from typing import Any, cast

from lark import Token, Tree

from py2cpp.ast.entry import Entry
from py2cpp.lang.implementation import implements


class EntryOfLark(Entry):
	"""エントリーへの要素アクセスを代替するプロクシー"""

	def __init__(self, entry: Tree | Token | None) -> None:
		"""インスタンスを生成

		Args:
			entry (Tree | Token | None): エントリー
		"""
		self.__entry = entry

	@property
	@implements
	def source(self) -> Tree | Token | None:
		"""Tree | Token | None: オリジナルのエントリー"""
		return self.__entry

	@property
	@implements
	def name(self) -> str:
		"""str: エントリー名 @note: 空の場合を考慮"""
		if type(self.__entry) is Tree:
			return self.__entry.data
		elif type(self.__entry) is Token:
			return self.__entry.type
		else:
			return self.empty_name

	@property
	@implements
	def has_child(self) -> bool:
		"""bool: True = 子を持つエントリー"""
		return type(self.__entry) is Tree

	@property
	@implements
	def children(self) -> list[Entry]:
		"""list[Entry]: 配下のエントリーリスト"""
		return [EntryOfLark(in_entry) for in_entry in self.__entry.children] if type(self.__entry) is Tree else []

	@property
	@implements
	def is_terminal(self) -> bool:
		"""bool: True = 終端記号"""
		return type(self.__entry) is Token

	@property
	@implements
	def value(self) -> str:
		"""str: 終端記号の値"""
		return self.__entry.value if type(self.__entry) is Token else ''

	@property
	@implements
	def is_empty(self) -> bool:
		"""bool: True = 空

		Note:
			Grammarの定義上存在するが、構文解析の結果で空になったエントリー
			例えば以下の様な関数の定義の場合[parameters]が対象となり、引数がない関数の場合、エントリーとしては存在するが内容は空になる
			例) function_def: "def" name "(" [parameters] ")" "->" ":" block
		"""
		return self.__entry is None


class Serialization:
	@classmethod
	def dumps(cls, entry: Tree | Token) -> dict[str, Any]:
		return cast(dict[str, Any], cls.__dumps(entry))

	@classmethod
	def __dumps(cls, entry: Tree | Token | None) -> dict[str, Any] | None:
		if type(entry) is Tree:
			children: list[dict[str, Any] | None] = []
			for child in entry.children:
				children.append(cls.dumps(child))

			return {'data': str(entry.data), 'children': children}
		elif type(entry) is Token:
			return {'type': entry.type, 'value': entry.value}
		else:
			return None

	@classmethod
	def loads(cls, entry: dict[str, Any]) -> Tree | Token:
		return cast(Tree | Token, cls.__loads(entry))

	@classmethod
	def __loads(cls, entry: dict[str, Any]) -> Tree | Token | None:
		if type(entry) is dict and 'children' in entry:
			children: list[Tree | Token | None] = []
			for child in entry['children']:
				children.append(cls.loads(child))

			return Tree(entry['data'], children)
		elif type(entry) is dict and 'type' in entry:
			return Token(entry['type'], entry['value'])
		else:
			return None
