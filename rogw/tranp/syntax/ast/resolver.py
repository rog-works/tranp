from dataclasses import dataclass, field
from typing import Generic, TypeVar

from rogw.tranp.errors import LogicError

T = TypeVar('T')


@dataclass
class SymbolMapping(Generic[T]):
	"""シンボルマッピングデータ

	Attributes:
		T: マッピング対象の基底クラス
		symbols: 文字列とシンボル型のマッピング
		fallback: 未定義のシンボルを指定した際のフォールバック型
	"""

	symbols: dict[type[T], list[str]] = field(default_factory=dict)
	fallback: type[T] | None = None


class Resolver(Generic[T]):
	"""シンボル名と型のマッピング情報を管理。シンボル名から紐づく型を解決

	Attributes:
		T: マッピング対象の基底クラス
	"""

	@classmethod
	def load(cls, mapping: SymbolMapping[T]) -> 'Resolver[T]':
		"""設定データを元にインスタンスを生成

		Args:
			mapping: シンボルマッピングデータ
		Returns:
			Resolver[T]: 生成したインスタンス
		"""
		inst = cls()
		for ctor, symbols in mapping.symbols.items():
			for symbol in symbols:
				inst.register(symbol, ctor)

		inst.fallback(mapping.fallback)
		return inst

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__ctors: dict[str, list[type[T]]] = {}
		self.__fallback: type[T] | None = None

	@property
	def accepts(self) -> list[str]:
		"""list[str]: 受け入れ対象のシンボル名リスト"""
		return list(self.__ctors.keys())

	def can_resolve(self, symbol: str) -> bool:
		"""解決出来るか確認

		Args:
			symbol: シンボル名
		Returns:
			bool: True = 解決できる
		"""
		return symbol in self.__ctors

	def register(self, symbol: str, ctor: type[T]) -> None:
		"""シンボルと型のマッピングを登録

		Args:
			symbol: シンボル名
			ctor: 紐づける型
		"""
		if symbol not in self.__ctors:
			self.__ctors[symbol] = []

		self.__ctors[symbol].append(ctor)

	def unregister(self, symbol: str) -> None:
		"""シンボルと型のマッピングを解除

		Args:
			symbol: シンボル名
		"""
		if symbol in self.__ctors:
			del self.__ctors[symbol]

	def fallback(self, ctor: type[T] | None) -> None:
		"""シンボルが解決出来ない場合にフォールバックする型

		Args:
			ctor: フォールバック時の型
		"""
		self.__fallback = ctor

	def resolve(self, symbol: str) -> list[type[T]]:
		"""シンボルに紐づく型を解決

		Args:
			symbol: シンボル名
		Returns:
			list[type[T]]: 解決した型
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		if self.can_resolve(symbol):
			return self.__ctors[symbol]

		if self.__fallback:
			return [self.__fallback]

		raise LogicError(symbol)

	def clear(self) -> None:
		"""型マッピングを全て解除"""
		self.__ctors = {}
		self.__fallback = None
