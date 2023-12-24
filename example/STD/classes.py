from typing import Any, Iterator

from STD.annotation import alias


@alias('int')
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


@alias('float')
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


@alias('str')
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


@alias('bool')
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


@alias('tuple')
class Tuple: ...


@alias('list')
class List:
	def __init__(self, iterable: Iterator) -> None: ...
	def append(self, elem: Any) -> None: ...
	def insert(self, index: int, elem: Any) -> None: ...
	def pop(self, index: int = -1) -> Any: ...
	def reverse(self) -> None: ...


@alias('dict')
class Dict:
	def __init__(self, iterable: Iterator[tuple]) -> None: ...
	def keys(self) -> list: ...
	def values(self) -> list: ...
	def items(self) -> list[tuple]: ...


@alias('None')
class Null: ...


class Unknown: ...
