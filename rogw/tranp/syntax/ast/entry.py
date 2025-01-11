from abc import ABCMeta, abstractmethod
from typing import Any, TypedDict

from rogw.tranp.lang.annotation import implements

DictToken = TypedDict('DictToken', {'name': str, 'value': str})
DictTree = TypedDict('DictTree', {'name': str, 'children': list['DictTree | DictToken | None']})
DictTreeEntry = DictTree | DictToken | None

SourceMap = TypedDict('SourceMap', {'begin': tuple[int, int], 'end': tuple[int, int]})


class Entry(metaclass=ABCMeta):
	"""ASTの各要素に対応するエントリーの抽象基底クラス"""

	@property
	@abstractmethod
	def source(self) -> Any:
		"""Any: オリジナルのエントリー"""
		raise NotImplementedError()

	@property
	@abstractmethod
	def name(self) -> str:
		"""str: エントリー名 @note: 空の場合を考慮"""
		raise NotImplementedError()

	@property
	@abstractmethod
	def has_child(self) -> bool:
		"""bool: True = 子を持つエントリー"""
		raise NotImplementedError()

	@property
	@abstractmethod
	def children(self) -> list['Entry']:
		"""list[Entry]: 配下のエントリーリスト"""
		raise NotImplementedError()

	@property
	@abstractmethod
	def is_terminal(self) -> bool:
		"""bool: True = 終端記号"""
		raise NotImplementedError()

	@property
	@abstractmethod
	def value(self) -> str:
		"""str: 終端記号の値"""
		raise NotImplementedError()

	@property
	@abstractmethod
	def is_empty(self) -> bool:
		"""bool: True = 空

		Note:
			Grammarの定義上存在するが、構文解析の結果で空になったエントリー
			例えば以下の様な関数の定義の場合[parameters]が対象となり、引数がない関数の場合、エントリーとしては存在するが内容は空になる
			例) function_def: "def" name "(" [parameters] ")" "->" ":" block
		"""
		raise NotImplementedError()

	@property
	def source_map(self) -> SourceMap:
		"""SourceMap: ソースマップ

		Note:
			begin: 開始位置(行/列)
			end: 終了位置(行/列)
		"""
		return {'begin': (0, 0), 'end': (0, 0)}

	@property
	def empty_name(self) -> str:
		"""str: 空のエントリー名"""
		# XXX 定数化を検討
		return '__empty__'


class EntryOfDict(Entry):
	"""連想配列のエントリー実装"""

	def __init__(self, entry: DictTreeEntry) -> None:
		"""インスタンスを生成

		Args:
			entry: エントリー
		"""
		self.__entry = entry

	@property
	@implements
	def source(self) -> DictTreeEntry:
		"""DictTreeEntry: オリジナルのエントリー"""
		return self.__entry

	@property
	@implements
	def name(self) -> str:
		"""str: エントリー名 @note: 空の場合を考慮"""
		return self.__entry['name'] if self.__entry is not None else self.empty_name

	@property
	@implements
	def has_child(self) -> bool:
		"""bool: True = 子を持つエントリー"""
		return type(self.__entry) is dict and 'children' in self.__entry

	@property
	@implements
	def children(self) -> list['Entry']:
		"""list[Entry]: 配下のエントリーリスト"""
		if self.__entry is None or 'children' not in self.__entry:
			return []

		return [EntryOfDict(child) for child in self.__entry['children']]

	@property
	@implements
	def is_terminal(self) -> bool:
		"""bool: True = 終端記号"""
		return not self.has_child

	@property
	@implements
	def value(self) -> str:
		"""str: 終端記号の値"""
		if self.__entry is None or 'value' not in self.__entry:
			return ''

		return self.__entry['value']

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
