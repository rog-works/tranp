from typing import Self, TypeAlias

# String

class char(str): ...
class wchar_t(str): ...

# Digit

class digit(int):
	def __eq__(self, other: Self | int | float | bool) -> bool:
		return self == other

	def __ne__(self, other: Self | int | float | bool) -> bool:
		return not self.__eq__(other)

	def __lt__(self, other: Self | int | float | bool) -> bool:
		return self < other

	def __gt__(self, other: Self | int | float | bool) -> bool:
		return self > other

	def __le__(self, other: Self | int | float | bool) -> bool:
		return self <= other

	def __ge__(self, other: Self | int | float | bool) -> bool:
		return self >= other

	def __add__(self, other: Self | int | bool) -> Self:
		return self + other

	def __sub__(self, other: Self | int | bool) -> Self:
		return self - other

	def __mul__(self, other: Self | int | bool) -> Self:
		return self * other

	def __truediv__(self, other: Self | int | bool) -> float:
		return self / other

	def __mod__(self, other: Self | int | bool) -> Self:
		return self % other

	def __and__(self, other: Self | int | bool) -> Self:
		return self & other

	def __or__(self, other: Self | int | bool) -> Self:
		return self | other

	def __xor__(self, other: Self | int | bool) -> Self:
		return self ^ other

	def __lshift__(self, n: int) -> Self:
		return self << n

	def __rshift__(self, n: int) -> Self:
		return self >> n


class byte(digit): ...
class int8(digit): ...
class uint8(digit): ...
class int32(digit): ...
class int64(digit): ...
class uint32(digit): ...
class uint64(digit): ...

# Decimal

class double(float):
	def __eq__(self, other: Self | int | float | bool) -> bool:
		return self == other

	def __ne__(self, other: Self | int | float | bool) -> bool:
		return not self.__eq__(other)

	def __lt__(self, other: Self | int | float | bool) -> bool:
		return self < other

	def __gt__(self, other: Self | int | float | bool) -> bool:
		return self > other

	def __le__(self, other: Self | int | float | bool) -> bool:
		return self <= other

	def __ge__(self, other: Self | int | float | bool) -> bool:
		return self >= other

	def __add__(self, other: Self | int | float | bool) -> Self:
		return self + other

	def __sub__(self, other: Self | int | float | bool) -> Self:
		return self - other

	def __mul__(self, other: Self | int | float | bool) -> Self:
		return self * other

	def __truediv__(self, other: Self | int | float | bool) -> Self:
		return self / other

	def __mod__(self, other: Self | int | float | bool) -> Self:
		return self % other

# Object

# XXX 本質的には正しくないが、void*としてのみ使用するため、これによって無駄なキャストを軽減
void: TypeAlias = object
