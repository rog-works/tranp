from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

from rogw.tranp.syntax.ast.entry import SourceMap

T = TypeVar('T')


class Query(Generic[T], metaclass=ABCMeta):
	"""パスベースのクエリーインターフェイス

	Attributes:
		T: クエリーによって取得するデータの基底クラス
	"""

	@abstractmethod
	def exists(self, full_path: str) -> bool:
		"""指定のパスに紐づく一意なノードが存在するか判定

		Args:
			full_path: フルパス
		Returns:
			True = 存在
		"""
		raise NotImplementedError()

	@abstractmethod
	def by(self, full_path: str) -> T:
		"""指定のパスに紐づく一意なエントリーをフェッチ

		Args:
			full_path: フルパス
		Returns:
			エントリー
		Raises:
			NotFoundError: エントリーが存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def parent(self, via: str) -> T:
		"""指定のパスを子として親のエントリーをフェッチ

		Args:
			via: 基点のパス(フルパス)
		Returns:
			データ
		Raises:
			NotFoundError: 親が存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def ancestor(self, via: str, tag: str) -> T:
		"""指定のエントリータグを持つ直近の親エントリーをフェッチ

		Args:
			via: 基点のパス
			tag: エントリータグ
		Returns:
			ノード
		Raises:
			NotFoundError: 指定のエントリータグを持つ親が存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def siblings(self, via: str) -> list[T]:
		"""指定のパスを基準に同階層のエントリーをフェッチ

		Args:
			via: 基点のパス(フルパス)
		Returns:
			エントリーリスト
		Raises:
			NotFoundError: 基点のエントリーが存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def children(self, via: str) -> list[T]:
		"""指定のパスを基準に1階層下のエントリーをフェッチ

		Args:
			via: 基点のパス(フルパス)
		Returns:
			エントリーリスト
		Raises:
			NotFoundError: 基点のエントリーが存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def expand(self, via: str) -> list[T]:
		"""指定のパスから下に存在する展開が可能なエントリーをフェッチ

		Args:
			via: 基点のパス(フルパス)
		Returns:
			エントリーリスト
		Raises:
			NotFoundError: 基点のエントリーが存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def values(self, via: str) -> list[str]:
		"""指定のパス以下(基点を含む)のエントリーの値を取得

		Args:
			via: 基点のパス(フルパス)
		Returns:
			値リスト
		"""
		raise NotImplementedError()

	@abstractmethod
	def id(self, full_path: str) -> int:
		"""指定のパスのエントリーのIDを取得

		Args:
			full_path: フルパス
		Returns:
			ID
		"""
		raise NotImplementedError()

	@abstractmethod
	def source_map(self, full_path: str) -> SourceMap:
		"""指定のパスのエントリーのソースマップを取得

		Args:
			full_path: フルパス
		Returns:
			ソースマップ
		"""
		raise NotImplementedError()
