from abc import ABCMeta, abstractmethod
from typing import Any


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
	def empty_name(self) -> str:
		"""str: 空のエントリー名"""
		# XXX 定数化を検討
		return '__empty__'
