from typing import Self, TypeAlias

# String

class char(str): ...
class wchar_t(str): ...

# Digit

class digit(int):
	"""Note: XXX タイプヒントで型名を取得するためクラスとして実装"""

	def __hash__(self) -> int:
		return self

	def __eq__(self, other: Self | int | float | bool) -> bool:
		return super().__eq__(other)

	def __ne__(self, other: Self | int | float | bool) -> bool:
		return super().__ne__(other)

	def __lt__(self, other: Self | int | float | bool) -> bool:
		return super().__lt__(int(other))

	def __gt__(self, other: Self | int | float | bool) -> bool:
		return super().__gt__(int(other))

	def __le__(self, other: Self | int | float | bool) -> bool:
		return super().__le__(int(other))

	def __ge__(self, other: Self | int | float | bool) -> bool:
		return super().__ge__(int(other))

	def __add__(self, other: Self | int | bool) -> Self:
		return self.__class__(super().__add__(other))

	def __sub__(self, other: Self | int | bool) -> Self:
		return self.__class__(super().__sub__(other))

	def __mul__(self, other: Self | int | bool) -> Self:
		return self.__class__(super().__mul__(other))

	def __truediv__(self, other: Self | int | bool) -> float:
		return self.__class__(super().__truediv__(other))

	def __mod__(self, other: Self | int | bool) -> Self:
		return self.__class__(super().__mod__(other))

	def __and__(self, other: Self | int | bool) -> Self:
		return self.__class__(super().__and__(other))

	def __or__(self, other: Self | int | bool) -> Self:
		return self.__class__(super().__or__(other))

	def __xor__(self, other: Self | int | bool) -> Self:
		return self.__class__(super().__xor__(other))

	def __lshift__(self, n: int) -> Self:
		return self.__class__(super().__lshift__(n))

	def __rshift__(self, n: int) -> Self:
		return self.__class__(super().__rshift__(n))


class byte(digit): ...
class int8(digit): ...
class uint8(digit): ...
class int32(digit): ...
class int64(digit): ...
class uint32(digit): ...
class uint64(digit): ...

# Decimal

class double(float):
	"""Note: XXX タイプヒントで型名を取得するためクラスとして実装"""

	def __eq__(self, other: Self | int | float | bool) -> bool:
		return super().__eq__(other)

	def __ne__(self, other: Self | int | float | bool) -> bool:
		return super().__ne__(other)

	def __lt__(self, other: Self | int | float | bool) -> bool:
		return super().__lt__(int(other))

	def __gt__(self, other: Self | int | float | bool) -> bool:
		return super().__gt__(int(other))

	def __le__(self, other: Self | int | float | bool) -> bool:
		return super().__le__(int(other))

	def __ge__(self, other: Self | int | float | bool) -> bool:
		return super().__ge__(int(other))

	def __add__(self, other: Self | int | float | bool) -> Self:
		return self.__class__(super().__add__(other))

	def __sub__(self, other: Self | int | float | bool) -> Self:
		return self.__class__(super().__sub__(other))

	def __mul__(self, other: Self | int | float | bool) -> Self:
		return self.__class__(super().__mul__(other))

	def __truediv__(self, other: Self | float | int | bool) -> float:
		return self.__class__(super().__truediv__(other))

	def __mod__(self, other: Self | float | int | bool) -> Self:
		return self.__class__(super().__mod__(other))

# Object

# XXX 本質的には正しくないが、void*としてのみ使用するため、これによって無駄なキャストを軽減
void: TypeAlias = object
