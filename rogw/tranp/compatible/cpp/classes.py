from typing import Self, TypeAlias

# String

class char(str): ...
class wchar_t(str): ...

# Digit

class digit(int):
	"""int系統の基底クラス"""

	def __hash__(self) -> int:
		"""Returns: ハッシュ値"""
		return id(self)

	def __eq__(self, other: int | Self) -> bool:
		"""other: 対象 Returns: 演算結果"""
		return int(self) == other

	def __ne__(self, other: int | Self) -> bool:
		"""other: 対象 Returns: 演算結果"""
		return int(self) != other

	def __lt__(self, other: int | Self) -> bool:
		"""other: 対象 Returns: 演算結果"""
		return int(self) < other

	def __gt__(self, other: int | Self) -> bool:
		"""other: 対象 Returns: 演算結果"""
		return int(self) > other

	def __le__(self, other: int | Self) -> bool:
		"""other: 対象 Returns: 演算結果"""
		return int(self) <= other

	def __ge__(self, other: int | Self) -> bool:
		"""other: 対象 Returns: 演算結果"""
		return int(self) >= other

	def __or__(self, other: int | Self) -> Self:
		"""other: 対象 Returns: 演算結果"""
		return self.__class__(int(self) | other)

	def __xor__(self, other: int | Self) -> Self:
		"""other: 対象 Returns: 演算結果"""
		return self.__class__(int(self) ^ other)

	def __and__(self, other: int | Self) -> Self:
		"""other: 対象 Returns: 演算結果"""
		return self.__class__(int(self) & other)

	def __lshift__(self, n: int) -> Self:
		"""n: シフト数 Returns: 演算結果"""
		return self.__class__(int(self) << n)

	def __rshift__(self, n: int) -> Self:
		"""n: シフト数 Returns: 演算結果"""
		return self.__class__(int(self) >> n)

	def __add__(self, other: int | Self) -> Self:
		"""other: 対象 Returns: 演算結果"""
		return self.__class__(int(self) + other)

	def __sub__(self, other: int | Self) -> Self:
		"""other: 対象 Returns: 演算結果"""
		return self.__class__(int(self) - other)

	def __mul__(self, other: int | Self) -> Self:
		"""other: 対象 Returns: 演算結果"""
		return self.__class__(int(self) * other)

	def __truediv__(self, other: int | Self) -> Self:
		"""other: 対象 Returns: 演算結果"""
		return self.__class__(int(self) / other)

	def __mod__(self, other: int | Self) -> Self:
		"""other: 対象 Returns: 演算結果"""
		return self.__class__(int(self) % other)


class byte(digit): ...
class int8(digit): ...
class uint8(digit): ...
class int32(digit): ...
class int64(digit): ...
class uint32(digit): ...
class uint64(digit): ...

# Decimal

class double(float): ...

# XXX 本質的には正しくないが、void*としてのみ使用するため、これによって無駄なキャストを軽減
void: TypeAlias = object
