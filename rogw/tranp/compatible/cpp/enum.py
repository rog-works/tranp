from enum import Enum
from typing import Self

from rogw.tranp.compatible.cpp.convertion import CastAddrProtocol, T
from rogw.tranp.compatible.cpp.object import CP
from rogw.tranp.lang.annotation import duck_typed


class CEnum(Enum):
	"""C言語との互換用Enum"""

	def __int__(self) -> int:
		"""Returns: 値(int)"""
		return int(self.value)

	def __eq__(self, other: Self | int) -> bool:
		"""Args: other: 対象 Returns: True = 一致"""
		if other.__class__ is int:
			return self.value == other
		else:
			return super().__eq__(other)

	def __or__(self, other: Self) -> Self:
		"""Args: other: 対象 Returns: 演算結果(OR)"""
		if isinstance(other, self.__class__):
			return self.value | other.value
		else:
			return self.value | other

	def __ror__(self, other: Self) -> Self:
		"""Args: other: 対象 Returns: 演算結果(OR/右)"""
		if isinstance(other, self.__class__):
			return self.value | other.value
		else:
			return self.value | other

	def __hash__(self) -> int:
		"""Returns: ハッシュ値"""
		return self.value

	@duck_typed(CastAddrProtocol)
	def __cast_addr__(self, to_origin: type[T]) -> CP[T]:
		"""アドレス型を安全に変換。変換先が不正な場合は例外を出力

		Args:
			to_origin: 変換先の実体のクラス
		Returns:
			変換後のアドレス変数
		Raises:
			ValueError: 不正な変換先を指定
		Note:
			XXX 本来サブクラスへの変換は不正だが、想定している変換先はC++用の数値型のみであるため簡易的な判定とする
			@see rogw.tranp.compatible.cpp.classes
		"""
		assert issubclass(to_origin, int), f'Not allowed convertion. to: {to_origin}'
		return CP(self.value)
