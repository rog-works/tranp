from enum import Enum
from typing import Any, TypeVar

T_Self = TypeVar('T_Self', bound='CEnum')


class CEnum(Enum):
	"""C言語との互換用Enum"""

	def __int__(self) -> int:
		"""int型へキャスト

		Returns:
			int: 数値
		"""
		return int(self.value)

	def __eq__(self, other: Any) -> bool:
		"""比較演算

		Args:
			other (Any): 対象
		Returns:
			bool: True = 同じ
		"""
		if type(other) is int:
			return self.value == other

		return super().__eq__(other)

	def __or__(self, other: T_Self) -> T_Self:
		"""ビット演算(OR)

		Args:
			other (T_Self): 対象
		Returns:
			T_Self: 演算結果
		"""
		return self.value | other.value

	def __hash__(self) -> int:
		"""インスタンスのハッシュ値を返す

		Returns:
			int: ID
		Note:
			dictのキーとして使えるようになる
		"""
		return id(self)
