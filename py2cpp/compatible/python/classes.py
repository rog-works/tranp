from typing import Any, Generic, Sequence

from py2cpp.compatible.python.embed import __actual__, __alias__
from py2cpp.compatible.python.template import T_Seq


# Type

class Iterator(Generic[T_Seq]):
	def __next__(self) -> T_Seq:
		...


class Union: ...
class Unknown: ...

# Primitive

@__actual__('int')
class Integer:
	# comparison
	def __eq__(self, other: Any) -> bool: ...
	def __ne__(self, other: Any) -> bool: ...
	def __lt__(self, other: int | float) -> bool: ...
	def __gt__(self, other: int | float) -> bool: ...
	# arithmetic
	def __add__(self, other: int) -> int: ...
	def __sub__(self, other: int) -> int: ...
	def __mul__(self, other: int) -> int: ...
	def __truediv__(self, other: int | float) -> float: ...  # XXX intを割ると必ずfloatになるので、実際は`n.__float__().__truediv__(other)`になるのでは？
	# bitwise
	def __and__(self, other: int) -> int: ...
	def __or__(self, other: int) -> int: ...
	# conversion
	def __int__(self) -> int: ...
	def __float__(self) -> float: ...
	def __str__(self) -> str: ...


@__actual__('float')
class Float:
	# comparison
	def __eq__(self, other: Any) -> bool: ...
	def __ne__(self, other: Any) -> bool: ...
	def __lt__(self, other: int | float) -> bool: ...
	def __gt__(self, other: int | float) -> bool: ...
	# arithmetic
	def __add__(self, other: int | float) -> float: ...
	def __sub__(self, other: int | float) -> float: ...
	def __mul__(self, other: int | float) -> float: ...
	def __truediv__(self, other: int | float) -> float: ...
	# conversion
	def __int__(self) -> int: ...
	def __float__(self) -> float: ...
	def __str__(self) -> str: ...


@__actual__('str')
class String:
	def split(self, delimiter: str) -> list[str]: ...
	def join(self, iterable: Iterator) -> str: ...
	def replace(self, subject: str, replaced: str) -> str: ...
	def find(self, subject: str) -> int: ...
	# comparison
	def __eq__(self, other: Any) -> bool: ...
	def __ne__(self, other: Any) -> bool: ...
	def __lt__(self, other: str) -> bool: ...
	def __gt__(self, other: str) -> bool: ...
	# arithmetic
	def __add__(self, other: str) -> float: ...
	def __mul__(self, other: int | str) -> float: ...
	# conversion
	def __int__(self) -> int: ...
	def __float__(self) -> float: ...
	def __str__(self) -> str: ...


@__actual__('bool')
class Boolean:
	# comparison
	def __eq__(self, other: Any) -> bool: ...
	def __ne__(self, other: Any) -> bool: ...
	def __lt__(self, other: int | float | bool) -> bool: ...
	def __gt__(self, other: int | float | bool) -> bool: ...
	# arithmetic
	# def __add__(self, other: T(int, float, bool)) -> T: ...  # XXX いずれも暗黙キャストされると予想
	# def __sub__(self, other: T(int, float, bool)) -> T: ...
	# def __mul__(self, other: T(int, float, bool)) -> T: ...
	def __truediv__(self, other: int | float | bool) -> float: ...
	# conversion
	def __int__(self) -> int: ...
	def __float__(self) -> float: ...
	def __str__(self) -> str: ...


@__actual__('tuple')
class Tuple: ...
@__actual__('pair_')
class Pair: ...


@__actual__('list')
class List(Generic[T_Seq]):
	def __init__(self, iterable: Iterator[T_Seq]) -> None: ...
	def __iter__(self) -> Iterator[T_Seq]: ...
	@__alias__('push_back')
	def append(self, elem: T_Seq) -> None: ...
	def pop(self, index: int = -1) -> T_Seq: ...


@__actual__('dict')
class Dict:
	def __init__(self, iterable: Iterator[tuple]) -> None: ...
	def keys(self) -> list: ...
	def values(self) -> list: ...
	def items(self) -> list[tuple]: ...


@__actual__('None')
class Null: ...

# Class

@__actual__('type')
class Type: ...
@__actual__('super')
class Super: ...
class Exception: ...

# Function

def id(instance: Any) -> int: ...
def print(*args: Any) -> None: ...
def enumerate(iterable: Sequence[Any]) -> Iterator[tuple[int, Any]]: ...  # XXX (Sequence[T]) -> Iterator[tuple[int, T]]
def range(size: int) -> Iterator[int]: ...
def len(iterable: Sequence[Any]) -> int: ...
