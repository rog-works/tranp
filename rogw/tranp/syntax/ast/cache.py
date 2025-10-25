from typing import Generic, TypeVar

from rogw.tranp.dsn.dsn import DSN
from rogw.tranp.errors import Errors

T = TypeVar('T')


class EntryCache(Generic[T]):
	"""エントリーキャッシュ"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__entries: dict[str, T] = {}
		self.__children: dict[str, dict[str, bool]] = {}
		self.__indexs: dict[str, int] = {}

	def exists(self, full_path: str) -> bool:
		"""指定のパスのエントリーが存在するか判定

		Args:
			full_path: フルパス
		Returns:
			True = 存在する
		"""
		return full_path in self.__entries

	def index_of(self, full_path: str) -> int:
		"""指定のパスのエントリーのインデックスを取得

		Args:
			full_path: フルパス
		Returns:
			インデックス
		"""
		return self.__indexs[full_path] if self.exists(full_path) else -1

	def by(self, full_path: str) -> T:
		"""指定のパスのエントリーをフェッチ

		Args:
			full_path: フルパス
		Returns:
			エントリー
		Raises:
			Errors.NodeNotFound: 存在しないパスを指定
		"""
		if not self.exists(full_path):
			raise Errors.NodeNotFound(full_path)

		return self.__entries[full_path]

	def group_by(self, via: str, depth: int = -1) -> dict[str, T]:
		"""指定の基準パス以下のエントリーをフェッチ

		Args:
			via: 基準のパス(フルパス)
			depth: 探索深度。-1は無制限(default = -1)
		Returns:
			(フルパス, エントリー)
		Raises:
			Errors.NodeNotFound: 存在しないパスを指定
		"""
		if not self.exists(via):
			raise Errors.NodeNotFound(via)

		if depth == 0:
			return {}

		entries = {via: self.by(via)}
		for key in self.__children[via]:
			path = DSN.join(via, key)
			entries[path] = self.by(path)
			entries.update(self.group_by(path, depth - 1))

		return entries

	def add(self, full_path: str, entry: T) -> None:
		"""指定のパスとエントリーを紐付けてキャッシュに追加

		Args:
			full_path: フルパス
			entry: エントリー
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
			if in_path not in self.__children:
				self.__children[in_path] = {}

			self.__children[in_path][last] = True
			last = remain.pop()
