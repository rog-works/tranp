from typing import Generic, TypeVar

from py2cpp.ast.dsn import DSN
from py2cpp.errors import NotFoundError

T = TypeVar('T')


class EntryCache(Generic[T]):
	"""エントリーキャッシュ"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__entries: dict[str, T] = {}
		self.__indexs: dict[str, dict[str, str]] = {}

	def exists(self, full_path: str) -> bool:
		"""指定のパスのエントリーが存在するか判定

		Args:
			full_path (str): フルパス
		Returns:
			bool: True = 存在する
		"""
		return full_path in self.__entries

	def by(self, full_path: str) -> T:
		"""指定のパスのエントリーをフェッチ

		Args:
			full_path (str): フルパス
		Returns:
			T: エントリー
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
		"""
		if not self.exists(via):
			raise NotFoundError(via)

		if depth == 0:
			return {}

		entries: dict[str, T] = {via: self.by(via)}
		for key in self.__indexs[via]:
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

		self.__entries[full_path] = entry
		self.__indexs[full_path] = {}

		elems = full_path.split('.')
		remain = elems[:-1]
		last = elems[-1]
		while len(remain):
			in_path = '.'.join(remain)
			self.__indexs[in_path] = {**(self.__indexs[in_path] if in_path in self.__indexs else {}), last: ''}
			last = remain.pop()
