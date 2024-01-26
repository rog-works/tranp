from typing import Any, Generic, Iterator, Sequence

from py2cpp.compatible.python.embed import __actual__
from py2cpp.compatible.python.template import T_Seq

# Primitive

@__actual__('int')
class Integer: ...
@__actual__('float')
class Float: ...
@__actual__('str')
class String: ...
@__actual__('bool')
class Boolean: ...
@__actual__('tuple')
class Tuple: ...
@__actual__('pair_')
class Pair: ...
@__actual__('list')
class List(Generic[T_Seq]):
	def append(self, elem: T_Seq) -> None: ...

@__actual__('dict')
class Dict: ...
@__actual__('None')
class Null: ...

# Type

class Union: ...
class Unknown: ...

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
