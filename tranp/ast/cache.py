from typing import Generic, TypeVar

from tranp.ast.dsn import DSN
from tranp.errors import NotFoundError

T = TypeVar('T')


class EntryCache(Generic[T]):
	"""エントリーキャッシュ"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__entries: dict[str, T] = {}
		self.__children: dict[str, dict[str, str]] = {}
		self.__indexs: dict[str, int] = {}

	def exists(self, full_path: str) -> bool:
		"""指定のパスのエントリーが存在するか判定

		Args:
			full_path (str): フルパス
		Returns:
			bool: True = 存在する
		"""
		return full_path in self.__entries

	def index_of(self, full_path: str) -> int:
		"""指定のパスのエントリーのインデックスを取得

		Args:
			full_path (str): フルパス
		Returns:
			int: インデックス
		"""
		return self.__indexs[full_path] if self.exists(full_path) else -1

	def by(self, full_path: str) -> T:
		"""指定のパスのエントリーをフェッチ

		Args:
			full_path (str): フルパス
		Returns:
			T: エントリー
		Raises:
			NotFoundError: 存在しないパスを指定
		"""
		if not self.exists(full_path):
			raise NotFoundError(full_path)

		return self.__entries[full_path]

	def group_by(self, via: str, depth: int = -1) -> dict[str, T]:
		"""指定の基準パス以下のエントリーをフェッチ

		Args:
			via (str): 基準のパス(フルパス)
			depth (int): 探索深度。-1は無制限(default = -1)
		Returns:
			dict[str, T]: (フルパス, エントリー)
		Raises:
			NotFoundError: 存在しないパスを指定
		"""
		if not self.exists(via):
			raise NotFoundError(via)

		if depth == 0:
			return {}

		entries: dict[str, T] = {via: self.by(via)}
		for key in self.__children[via]:
			path = DSN.join(via, key)
			entries[path] = self.by(path)
			under = self.group_by(path, depth - 1)
			entries = {**entries, **under}

		return entries

	def add(self, full_path: str, entry: T) -> None:
		"""指定のパスとエントリーを紐付けてキャッシュに追加

		Args:
			full_path (str): フルパス
			entry (T): エントリー
		"""
		if self.exists(full_path):
			return

		self.__indexs[full_path] = len(self.__entries)
		self.__entries[full_path] = entry
		self.__children[full_path] = {}

		elems = full_path.split('.')
		remain = elems[:-1]
		last = elems[-1]
		while len(remain):
			in_path = '.'.join(remain)
			self.__children[in_path] = {**(self.__children[in_path] if in_path in self.__children else {}), last: ''}
			last = remain.pop()
