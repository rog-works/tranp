from typing import Any, Generic, Iterator, Sequence

from rogw.tranp.compatible.python.embed import __actual__, __alias__
from rogw.tranp.compatible.python.template import T_Seq, T_Key


# Type

class Union: ...
class Unknown: ...

# Primitive

@__actual__('int')
class Integer:
	def __init__(self, value: int | float | bool) -> None: ...
	# comparison
	def __eq__(self, other: int | float | bool) -> bool: ...
	def __ne__(self, other: int | float | bool) -> bool: ...
	def __lt__(self, other: int | float | bool) -> bool: ...
	def __gt__(self, other: int | float | bool) -> bool: ...
	# arithmetic
	def __add__(self, other: int | bool) -> int: ...
	def __sub__(self, other: int | bool) -> int: ...
	def __mul__(self, other: int | bool) -> int: ...
	# bitwise
	def __and__(self, other: int | bool) -> int: ...
	def __or__(self, other: int | bool) -> int: ...
	# conversion
	def __int__(self) -> int: ...
	def __float__(self) -> float: ...
	def __str__(self) -> str: ...


@__actual__('float')
class Float:
	def __init__(self, value: int | float | bool) -> None: ...
	# comparison
	def __eq__(self, other: int | float | bool) -> bool: ...
	def __ne__(self, other: int | float | bool) -> bool: ...
	def __lt__(self, other: int | float | bool) -> bool: ...
	def __gt__(self, other: int | float | bool) -> bool: ...
	# arithmetic
	def __add__(self, other: int | float | bool) -> float: ...
	def __sub__(self, other: int | float | bool) -> float: ...
	def __mul__(self, other: int | float | bool) -> float: ...
	def __truediv__(self, other: int | float | bool) -> float: ...
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
	def __eq__(self, other: str) -> bool: ...
	def __ne__(self, other: str) -> bool: ...
	def __lt__(self, other: str) -> bool: ...
	def __gt__(self, other: str) -> bool: ...
	# arithmetic
	def __add__(self, other: str) -> str: ...
	def __mul__(self, other: int) -> str: ...
	# conversion
	def __int__(self) -> int: ...
	def __float__(self) -> float: ...
	def __str__(self) -> str: ...


@__actual__('bool')
class Boolean:
	# comparison
	def __eq__(self, other: int | float | bool) -> bool: ...
	def __ne__(self, other: int | float | bool) -> bool: ...
	def __lt__(self, other: int | float | bool) -> bool: ...
	def __gt__(self, other: int | float | bool) -> bool: ...
	# conversion
	def __int__(self) -> int: ...
	def __float__(self) -> float: ...
	def __str__(self) -> str: ...


@__actual__('tuple')
class Tuple: ...
class Pair(Generic[T_Key, T_Seq]): ...


@__actual__('list')
class List(Generic[T_Seq]):
	def __init__(self, iterable: Iterator[T_Seq]) -> None: ...
	def __iter__(self) -> Iterator[T_Seq]: ...
	@__alias__('push_back')
	def append(self, elem: T_Seq) -> None: ...
	def pop(self, index: int = -1) -> T_Seq: ...


@__actual__('dict')
class Dict(Generic[T_Key, T_Seq]):
	def __init__(self, iterable: Iterator[Pair[T_Key, T_Seq]]) -> None: ...
	def keys(self) -> Iterator[T_Key]: ...
	def values(self) -> Iterator[T_Seq]: ...
	def items(self) -> Iterator[Pair[T_Key, T_Seq]]: ...


@__actual__('None')
class Null: ...

# Class

@__actual__('object')
class Object:
	def __init__(self) -> None: ...


@__actual__('type')
class Type: ...
@__actual__('super')
class Super: ...
class Exception:
	def __init__(self, *args: Any) -> None: ...

# Function

def id(instance: Any) -> int: ...
def print(*args: Any) -> None: ...
def enumerate(iterable: Sequence[T_Seq]) -> Iterator[tuple[int, T_Seq]]: ...
def range(size: int) -> Iterator[int]: ...
def len(iterable: Sequence[Any]) -> int: ...
