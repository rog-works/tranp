from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from py2cpp.errors import LogicError

T = TypeVar('T')


@dataclass
class Settings(Generic[T]):
	"""マッピング設定データ

	Attributes:
		T: マッピング対象の基底クラス
	"""

	symbols: dict[str, type[T]] = field(default_factory=dict)
	fallback: type[T] | None = None


class Resolver(Generic[T]):
	"""シンボル名と型のマッピング情報を管理。シンボル名から紐づく型を解決

	Attributes:
		T: マッピング対象の基底クラス
	"""

	@classmethod
	def load(cls, settings: Settings[T]) -> 'Resolver[T]':
		"""設定データを元にインスタンスを生成

		Args:
			settings (Settings[T]): 設定データ
		Returns:
			Resolver[T]: 生成したインスタンス
		"""
		inst = cls()
		for symbol, ctor in settings.symbols.items():
			inst.register(symbol, ctor)

		inst.fallback(settings.fallback)
		return inst

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__ctors: dict[str, type[T]] = {}
		self.__fallback: type[T] | None = None

	@property
	def accepts(self) -> list[str]:
		"""list[str]: 受け入れ対象のシンボル名リスト"""
		return list(self.__ctors.keys())

	def can_resolve(self, symbol: str) -> bool:
		"""解決出来るか確認

		Args:
			symbol (str): シンボル名
		Returns:
			bool: True = 解決できる
		"""
		return symbol in self.__ctors

	def register(self, symbol: str, ctor: type[T]) -> None:
		"""シンボルと型のマッピングを登録

		Args:
			symbol (str): シンボル名
			ctor (type[T]): 紐づける型
		"""
		self.__ctors[symbol] = ctor

	def unregister(self, symbol: str) -> None:
		"""シンボルと型のマッピングを解除

		Args:
			symbol (str): シンボル名
		"""
		if symbol in self.__ctors:
			del self.__ctors[symbol]

	def fallback(self, ctor: type[T] | None) -> None:
		"""シンボルが解決出来ない場合にフォールバックする型

		Args:
			ctor (type[T] | None): フォールバック時の型
		"""
		self.__fallback = ctor

	def resolve(self, symbol: str) -> type[T]:
		"""シンボルに紐づく型を解決

		Args:
			symbol (str): シンボル名
		Returns:
			type[T]: 解決した型
		Raises:
			LogicError: シンボルの解決に失敗
		"""
		if self.can_resolve(symbol):
			return self.__ctors[symbol]

		if self.__fallback:
			return self.__fallback

		raise LogicError(symbol)

	def clear(self) -> None:
		"""型マッピングを全て解除"""
		self.__ctors = {}
		self.__fallback = None


class Query(Generic[T], metaclass=ABCMeta):
	"""パスベースのクエリーインターフェイス

	Attributes:
		T: クエリーによって取得するデータの基底クラス
	"""

	@abstractmethod
	def exists(self, full_path: str) -> bool:
		"""指定のパスに紐づく一意なノードが存在するか判定

		Args:
			full_path (str): フルパス
		Returns:
			bool: True = 存在
		"""
		raise NotImplementedError()

	@abstractmethod
	def by(self, full_path: str) -> T:
		"""指定のパスに紐づく一意なエントリーをフェッチ

		Args:
			full_path (str): フルパス
		Returns:
			T: エントリー
		Raises:
			NotFoundError: エントリーが存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def parent(self, via: str) -> T:
		"""指定のパスを子として親のエントリーをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			T: データ
		Raises:
			NotFoundError: 親が存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def siblings(self, via: str) -> list[T]:
		"""指定のパスを基準に同階層のエントリーをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[T]: エントリーリスト
		Raises:
			NotFouneError: 基点のエントリーが存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def children(self, via: str) -> list[T]:
		"""指定のパスを基準に1階層下のエントリーをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[T]: エントリーリスト
		Raises:
			NotFouneError: 基点のエントリーが存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def leafs(self, via: str, leaf_name: str) -> list[T]:
		"""指定のパスから下に存在する接尾辞が一致するエントリーをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
			leaf_name (str): 接尾辞
		Returns:
			list[T]: エントリーリスト
		Raises:
			NotFouneError: 基点のエントリーが存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def expansion(self, via: str) -> list[T]:
		"""指定のパスから下に存在する展開が可能なエントリーをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[T]: エントリーリスト
		Raises:
			NotFouneError: 基点のエントリーが存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def by_value(self, full_path: str) -> str:
		"""指定のエントリーの値を取得

		Args:
			full_path (str): フルパス
		Returns:
			str: 値
		Raises:
			NotFouneError: エントリーが存在しない
		"""
		...

	# @abstractmethod
	# def embed(self, via: str, name: str) -> T:
	# 	"""指定のパスの下に仮想のエントリーを生成

	# 	Args:
	# 		via (str): 基点のパス(フルパス)
	# 		name (str): 仮想エントリーの名前
	# 	Returns:
	# 		T: 生成した仮想エントリー
	# 	"""
	# 	raise NotImplementedError()
