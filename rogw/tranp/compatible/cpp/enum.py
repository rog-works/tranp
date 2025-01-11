from enum import Enum
from typing import Self


class CEnum(Enum):
	"""C言語との互換用Enum"""

	def __int__(self) -> int:
		"""int型へキャスト

		Returns:
			int: 数値
		"""
		return int(self.value)

	def __eq__(self, other: Self | int) -> bool:
		"""比較演算

		Args:
			other: 対象
		Returns:
			bool: True = 同じ
		"""
		if other.__class__ is int:
			return self.value == other
		else:
			return super().__eq__(other)

	def __or__(self, other: Self) -> Self:
		"""ビット演算(OR)

		Args:
			other: 対象
		Returns:
			Self: 演算結果
		"""
		if isinstance(other, self.__class__):
			return self.value | other.value
		else:
			return self.value | other

	def __ror__(self, other: Self) -> Self:
		"""ビット演算(OR/右)

		Args:
			other: 対象
		Returns:
			Self: 演算結果
		"""
		if isinstance(other, self.__class__):
			return self.value | other.value
		else:
			return self.value | other

	def __hash__(self) -> int:
		"""インスタンスのハッシュ値を返す

		Returns:
			int: ID
		Note:
			dictのキーとして使えるようになる
		"""
		return id(self)
