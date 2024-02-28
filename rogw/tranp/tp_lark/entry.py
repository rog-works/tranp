from typing import cast

from lark import Token, Tree

from rogw.tranp.ast.entry import Entry, SourceMap, T_Entry, T_Tree
from rogw.tranp.lang.implementation import implements, override


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

	@property
	@override
	def source_map(self) -> SourceMap:
		"""SourceMap: ソースマップ

		Note:
			begin (tuple[int, int]): 開始位置(行/列)
			end (tuple[int, int]): 終了位置(行/列)
		"""
		if type(self.__entry) is Tree and self.__entry._meta is not None:
			return {
				'begin': (self.__entry._meta.line, self.__entry._meta.column),
				'end': (self.__entry._meta.end_line, self.__entry._meta.end_column),
			}
		elif type(self.__entry) is Token and self.__entry.line and self.__entry.column and self.__entry.end_line and self.__entry.end_column:
			return {
				'begin': (self.__entry.line, self.__entry.column),
				'end': (self.__entry.end_line, self.__entry.end_column),
			}
		else:
			return {'begin': (0, 0), 'end': (0, 0)}


class Serialization:
	@classmethod
	def dumps(cls, root: Tree) -> T_Tree:
		"""連想配列にシリアライズ

		Args:
			root (Tree): ツリー
		Returns:
			T_Tree: シリアライズツリー
		"""
		return cast(T_Tree, cls.__dumps(root))

	@classmethod
	def __dumps(cls, entry: Tree | Token | None) -> T_Entry:
		"""連想配列にシリアライズ

		Args:
			entry (Tree | Token | None): エントリー
		Returns:
			T_Entry: シリアライズエントリー
		"""
		if type(entry) is Tree:
			children: list[T_Entry] = []
			for child in entry.children:
				children.append(cls.__dumps(child))

			return {'name': str(entry.data), 'children': children}
		elif type(entry) is Token:
			return {'name': entry.type, 'value': entry.value}
		else:
			return None

	@classmethod
	def loads(cls, root: T_Tree) -> Tree:
		"""連想配列からデシリアライズ

		Args:
			root (T_Tree): シリアライズツリー
		Returns:
			Tree: ツリー
		"""
		return cast(Tree, cls.__loads(root))

	@classmethod
	def __loads(cls, entry: T_Entry) -> Tree | Token | None:
		"""連想配列からデシリアライズ

		Args:
			entry (T_Entry): シリアライズエントリー
		Returns:
			Tree | Token | None: エントリー
		"""
		if type(entry) is dict and 'children' in entry:
			children: list[Tree | Token | None] = []
			for child in cast(list[T_Entry], entry['children']):
				children.append(cls.__loads(child))

			return Tree(entry['name'], children)
		elif type(entry) is dict and 'value' in entry:
			return Token(entry['name'], entry['value'])
		else:
			return None
