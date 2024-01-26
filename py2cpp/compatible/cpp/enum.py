from enum import Enum as OrgEnum
from typing import Any


class Enum(OrgEnum):
	"""C言語との互換用Enum"""

	def __int__(self) -> int:
		"""int型へキャスト

		Returns:
			int: 数値
		"""
		return int(self.value)

	def __eq__(self, other: Any) -> bool:
		"""比較演算

		Returns:
			bool: True = 同じ
		Note:
			int型との比較を追加
		"""
		if type(other) is int:
			return self.value == other

		return super().__eq__(other)

	def __hash__(self) -> int:
		"""インスタンスのハッシュ値を返す

		Returns:
			int: ID
		Note:
			dictのキーとして使えるようになる
		"""
		return id(self)
