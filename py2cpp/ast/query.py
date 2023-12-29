from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

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
	def ancestor(self, via: str, tag: str) -> T:
		"""指定のエントリータグを持つ直近の親エントリーをフェッチ

		Args:
			via (str): 基点のパス
			tag (str): エントリータグ
		Returns:
			Node: ノード
		Raises:
			NotFoundError: 指定のエントリータグを持つ親が存在しない
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
			NotFoundError: 基点のエントリーが存在しない
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
			NotFoundError: 基点のエントリーが存在しない
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
			NotFoundError: 基点のエントリーが存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def expand(self, via: str) -> list[T]:
		"""指定のパスから下に存在する展開が可能なエントリーをフェッチ

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[T]: エントリーリスト
		Raises:
			NotFoundError: 基点のエントリーが存在しない
		"""
		raise NotImplementedError()

	@abstractmethod
	def values(self, full_path: str) -> list[str]:
		"""指定のパス以下(基点を含む)のエントリーの値を取得

		Args:
			via (str): 基点のパス(フルパス)
		Returns:
			list[str]: 値リスト
		"""
		raise NotImplementedError()
