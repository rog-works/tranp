from typing import TypeAlias, TypedDict, cast, override

import lark

from rogw.tranp.syntax.ast.entry import Entry, SourceMap
from rogw.tranp.lang.annotation import implements


class EntryOfLark(Entry):
	"""エントリーへの要素アクセスを代替するプロクシー"""

	def __init__(self, entry: lark.Tree | lark.Token | None) -> None:
		"""インスタンスを生成

		Args:
			entry: エントリー
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
			begin: 開始位置(行/列)
			end: 終了位置(行/列)
		"""
		if type(self.__entry) is lark.Tree and self.__entry.meta is not None and not self.__entry.meta.empty:
			source_map = (
				self.__entry.meta.line,
				self.__entry.meta.column,
				self.__entry.meta.end_line,
				self.__entry.meta.end_column,
			)
			return {'begin': (source_map[0], source_map[1]), 'end': (source_map[2], source_map[3])}
		elif type(self.__entry) is lark.Token and self.__entry.line and self.__entry.column and self.__entry.end_line and self.__entry.end_column:
			source_map = (
				self.__entry.line,
				self.__entry.column,
				self.__entry.end_line,
				self.__entry.end_column,
			)
			return {'begin': (source_map[0], source_map[1]), 'end': (source_map[2], source_map[3])}
		else:
			return {'begin': (0, 0), 'end': (0, 0)}


DumpSourceMap: TypeAlias = tuple[int, int, int, int]
DumpToken = TypedDict('DumpToken', {'name': str, 'value': str, 'source_map': DumpSourceMap})
DumpTree = TypedDict('DumpTree', {'name': str, 'children': list['DumpToken | DumpTree | None'], 'source_map': DumpSourceMap})
DumpTreeEntry = DumpToken | DumpTree | None


class Serialization:
	"""Larkエントリーのシリアライザー"""

	@classmethod
	def dumps(cls, root: lark.Tree) -> DumpTree:
		"""連想配列にシリアライズ

		Args:
			root: ツリー
		Returns:
			シリアライズツリー
		"""
		return cast(DumpTree, cls.__dumps(root))

	@classmethod
	def __dumps(cls, entry: lark.Tree | lark.Token | None) -> DumpTreeEntry:
		"""連想配列にシリアライズ

		Args:
			entry: エントリー
		Returns:
			シリアライズエントリー
		"""
		proxy = EntryOfLark(entry)
		source_map = (
			proxy.source_map['begin'][0],
			proxy.source_map['begin'][1],
			proxy.source_map['end'][0],
			proxy.source_map['end'][1],
		)
		if proxy.has_child:
			children: list[DumpTreeEntry] = []
			for child in proxy.children:
				children.append(cls.__dumps(child.source))

			return {'name': proxy.name, 'children': children, 'source_map': source_map}
		elif not proxy.is_empty:
			return {'name': proxy.name, 'value': proxy.value, 'source_map': source_map}
		else:
			return None

	@classmethod
	def loads(cls, root: DumpTree) -> lark.Tree:
		"""連想配列からデシリアライズ

		Args:
			root: シリアライズツリー
		Returns:
			ツリー
		"""
		return cast(lark.Tree, cls.__loads(root))

	@classmethod
	def __loads(cls, entry: DumpTreeEntry) -> lark.Tree | lark.Token | None:
		"""連想配列からデシリアライズ

		Args:
			entry: シリアライズエントリー
		Returns:
			エントリー
		"""
		if type(entry) is dict and 'children' in entry:
			entry_tree = cast(DumpTree, entry)
			children: list[lark.Tree | lark.Token | None] = []
			for child in cast(list[DumpTreeEntry], entry_tree['children']):
				children.append(cls.__loads(child))

			meta = lark.tree.Meta()
			meta.line = entry_tree['source_map'][0]
			meta.column = entry_tree['source_map'][1]
			meta.end_line = entry_tree['source_map'][2]
			meta.end_column = entry_tree['source_map'][3]
			meta.empty = False
			return lark.Tree(entry_tree['name'], children, meta)
		elif type(entry) is dict and 'value' in entry:
			entry_token = cast(DumpToken, entry)
			token = lark.Token(entry_token['name'], entry_token['value'])
			token.line = entry_token['source_map'][0]
			token.column = entry_token['source_map'][1]
			token.end_line = entry_token['source_map'][2]
			token.end_column = entry_token['source_map'][3]
			return token
		else:
			return None
