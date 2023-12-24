from typing import Generic, TypeVar

from py2cpp.errors import NotFoundError

T = TypeVar('T')


class EntryCache(Generic[T]):
	"""エントリーキャッシュ

	Note:
		グループ検索用のインデックスは、ツリーの先頭から順序通りに登録することが正常動作の必須要件
		効率よくインデックスを構築出来る反面、シンタックスツリーが静的であることを前提とした実装のため、
		インデックスを作り替えることは出来ず、登録順序にも強い制限がある
	"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.__entries: list[T] = []
		self.__indexs: dict[str, tuple[int, int]] = {}

	def exists(self, full_path: str) -> bool:
		"""指定のパスのエントリーが存在するか判定

		Args:
			full_path (str): フルパス
		Returns:
			bool: True = 存在する
		"""
		return full_path in self.__indexs

	def by(self, full_path: str) -> T:
		"""指定のパスのエントリーをフェッチ

		Args:
			full_path (str): フルパス
		Returns:
			T: エントリー
		"""
		if not self.exists(full_path):
			raise NotFoundError(full_path)

		begin, _ = self.__indexs[full_path]
		return self.__entries[begin]

	def group_by(self, via: str) -> dict[str, T]:
		"""指定の基準パス以下のエントリーをフェッチ

		Args:
			via (str): 基準のパス(フルパス)
		Returns:
			dict[str, T]: (フルパス, エントリー)
		"""
		if not self.exists(via):
			raise NotFoundError(via)

		begin, end = self.__indexs[via]
		items = self.__entries[begin:end + 1]
		keys = list(self.__indexs.keys())[begin:end + 1]
		return {keys[index]: items[index] for index in range((end + 1) - begin)}

	def add(self, full_path: str, entry: T) -> None:
		"""指定のパスとエントリーを紐付けてキャッシュに追加

		Args:
			full_path (str): フルパス
			entry (str): フルパス
		"""
		if self.exists(full_path):
			return

		begin = len(self.__entries)
		self.__entries.append(entry)
		self.__indexs[full_path] = (begin, begin)

		remain = full_path.split('.')[:-1]
		while len(remain):
			in_key = '.'.join(remain)
			begin, end = self.__indexs[in_key]
			self.__indexs[in_key] = (begin, end + 1)
			remain.pop()
