from typing import TypedDict, cast

import lark

from rogw.tranp.syntax.ast.entry import Entry, SourceMap
from rogw.tranp.lang.implementation import implements, override


class EntryOfLark(Entry):
	"""エントリーへの要素アクセスを代替するプロクシー"""

	def __init__(self, entry: lark.Tree | lark.Token | None) -> None:
		"""インスタンスを生成

		Args:
			entry (Tree | Token | None): エントリー
		"""
		self.__entry = entry

	@property
	@implements
	def source(self) -> lark.Tree | lark.Token | None:
		"""Tree | Token | None: オリジナルのエントリー"""
		return self.__entry

	@property
	@implements
	def name(self) -> str:
		"""str: エントリー名 @note: 空の場合を考慮"""
		if type(self.__entry) is lark.Tree:
			return self.__entry.data
		elif type(self.__entry) is lark.Token:
			return self.__entry.type
		else:
			return self.empty_name

	@property
	@implements
	def has_child(self) -> bool:
		"""bool: True = 子を持つエントリー"""
		return type(self.__entry) is lark.Tree

	@property
	@implements
	def children(self) -> list[Entry]:
		"""list[Entry]: 配下のエントリーリスト"""
		return [EntryOfLark(in_entry) for in_entry in self.__entry.children] if type(self.__entry) is lark.Tree else []

	@property
	@implements
	def is_terminal(self) -> bool:
		"""bool: True = 終端記号"""
		return type(self.__entry) is lark.Token

	@property
	@implements
	def value(self) -> str:
		"""str: 終端記号の値"""
		return self.__entry.value if type(self.__entry) is lark.Token else ''

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
		if type(self.__entry) is lark.Tree and self.__entry.meta is not None and not self.__entry.meta.empty:
			try:
				return {
					'begin': (self.__entry.meta.line, self.__entry.meta.column),
					'end': (self.__entry.meta.end_line, self.__entry.meta.end_column),
				}
			except Exception as e:
				raise
		elif type(self.__entry) is lark.Token and self.__entry.line and self.__entry.column and self.__entry.end_line and self.__entry.end_column:
			return {
				'begin': (self.__entry.line, self.__entry.column),
				'end': (self.__entry.end_line, self.__entry.end_column),
			}
		else:
			return {'begin': (0, 0), 'end': (0, 0)}


DictToken = TypedDict('DictToken', {'name': str, 'value': str, 'source_map': SourceMap})
DictTree = TypedDict('DictTree', {'name': str, 'children': list['DictToken | DictTree | None'], 'source_map': SourceMap})
DictTreeEntry = DictToken | DictTree | None


class Serialization:
	"""Larkエントリーのシリアライザー"""

	@classmethod
	def dumps(cls, root: lark.Tree) -> DictTree:
		"""連想配列にシリアライズ

		Args:
			root (lark.Tree): ツリー
		Returns:
			DictTree: シリアライズツリー
		"""
		return cast(DictTree, cls.__dumps(root))

	@classmethod
	def __dumps(cls, entry: lark.Tree | lark.Token | None) -> DictTreeEntry:
		"""連想配列にシリアライズ

		Args:
			entry (lark.Tree | lark.Token | None): エントリー
		Returns:
			DictTreeEntry: シリアライズエントリー
		"""
		proxy = EntryOfLark(entry)
		if proxy.has_child:
			children: list[DictTreeEntry] = []
			for child in proxy.children:
				children.append(cls.__dumps(child.source))

			return {'name': proxy.name, 'children': children, 'source_map': proxy.source_map}
		elif not proxy.is_empty:
			return {'name': proxy.name, 'value': proxy.value, 'source_map': proxy.source_map}
		else:
			return None

	@classmethod
	def loads(cls, root: DictTree) -> lark.Tree:
		"""連想配列からデシリアライズ

		Args:
			root (DictTree): シリアライズツリー
		Returns:
			lark.Tree: ツリー
		"""
		return cast(lark.Tree, cls.__loads(root))

	@classmethod
	def __loads(cls, entry: DictTreeEntry) -> lark.Tree | lark.Token | None:
		"""連想配列からデシリアライズ

		Args:
			entry (DictTreeEntry): シリアライズエントリー
		Returns:
			lark.Tree | lark.Token | None: エントリー
		"""
		if type(entry) is dict and 'children' in entry:
			children: list[lark.Tree | lark.Token | None] = []
			for child in cast(list[DictTreeEntry], entry['children']):
				children.append(cls.__loads(child))

			meta = lark.tree.Meta()
			meta.line = entry['source_map']['begin'][0]
			meta.column = entry['source_map']['begin'][1]
			meta.end_line = entry['source_map']['end'][0]
			meta.end_column = entry['source_map']['end'][1]
			meta.empty = False
			return lark.Tree(entry['name'], children, meta)
		elif type(entry) is dict and 'value' in entry:
			token = lark.Token(entry['name'], entry['value'])
			token.line = entry['source_map']['begin'][0]
			token.column = entry['source_map']['begin'][1]
			token.end_line = entry['source_map']['end'][0]
			token.end_column = entry['source_map']['end'][1]
			return token
		else:
			return None
