from typing import IO, Any, Callable, Generic, Iterator, Sequence

from rogw.tranp.compatible.python.template import T, T_Key, T_Value

# Embed

def __actual__(name: str) -> Callable[[T], T]:
	"""コード上で実際に用いる名称を埋め込む

	Args:
		name (str): 名前
	Returns:
		Callable[[T], T]: デコレート対象
	Examples:
		```python
		@__actual__('type')
		class Type: ...
		```
	"""
	def decorator(wrapped: T) -> T:
		return wrapped

	return decorator

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
	# FIXME other: Any
	def __not__(self, other: int | float | bool | str) -> bool: ...
	# arithmetic
	def __add__(self, other: int | bool) -> int: ...
	def __sub__(self, other: int | bool) -> int: ...
	def __mul__(self, other: int | bool) -> int: ...
	def __truediv__(self, other: int | bool) -> float: ...
	def __mod__(self, other: int | bool) -> int: ...
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
	# FIXME other: Any
	def __not__(self, other: int | float | bool | str) -> bool: ...
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
	def __init__(self, value: int | float) -> None: ...
	def split(self, delimiter: str) -> list[str]: ...
	def join(self, iterable: Iterator) -> str: ...
	def replace(self, subject: str, replaced: str) -> str: ...
	def find(self, subject: str) -> int: ...
	def rfind(self, subject: str) -> int: ...
	def startswith(self, subject: str) -> bool: ...
	def endswith(self, subject: str) -> bool: ...
	def format(self, format_text: str, *value: Any) -> str: ...
	# comparison
	def __eq__(self, other: str) -> bool: ...
	def __ne__(self, other: str) -> bool: ...
	def __lt__(self, other: str) -> bool: ...
	def __gt__(self, other: str) -> bool: ...
	# FIXME other: Any
	def __not__(self, other: int | float | bool | str) -> bool: ...
	# arithmetic
	def __add__(self, other: str) -> str: ...
	def __mul__(self, other: int) -> str: ...
	# conversion
	def __int__(self) -> int: ...
	def __float__(self) -> float: ...
	def __str__(self) -> str: ...


@__actual__('bool')
class Boolean:
	def __init__(self, value: int | float | bool) -> None: ...
	# comparison
	def __eq__(self, other: int | float | bool) -> bool: ...
	def __ne__(self, other: int | float | bool) -> bool: ...
	def __lt__(self, other: int | float | bool) -> bool: ...
	def __gt__(self, other: int | float | bool) -> bool: ...
	# FIXME other: Any
	def __not__(self, other: int | float | bool | str) -> bool: ...
	# arithmetic
	def __add__(self, other: bool) -> int: ...
	def __sub__(self, other: bool) -> int: ...
	def __mul__(self, other: bool) -> int: ...
	def __truediv__(self, other: bool) -> float: ...
	def __mod__(self, other: bool) -> int: ...
	# bitwise XXX これらの演算はあくまでもビット演算であり本質的には正しくない。が、結果的には問題ないので一旦この実装とする
	def __and__(self, other: bool) -> bool: ...
	def __or__(self, other: bool) -> bool: ...
	# conversion
	def __int__(self) -> int: ...
	def __float__(self) -> float: ...
	def __str__(self) -> str: ...


@__actual__('list')
class List(Sequence[T_Value]):
	def __init__(self, iterable: Iterator[T_Value]) -> None: ...
	def __iter__(self) -> Iterator[T_Value]: ...
	def __mul__(self, size: int) -> list[T_Value]: ...
	def __contains__(self, key: T_Value) -> bool: ...
	def append(self, elem: T_Value) -> None: ...
	def insert(self, index: int, elem: T_Value) -> None: ...
	def extend(self, iterable: Iterator[T_Value]) -> None: ...
	def remove(self, elem: T_Value) -> T_Value: ...
	def pop(self, index: int = -1) -> T_Value: ...


@__actual__('dict')
class Dict(Sequence[tuple[T_Key, T_Value]]):
	def __init__(self, iterable: Iterator[tuple[T_Key, T_Value]]) -> None: ...
	def __iter__(self) -> Iterator[T_Key]: ...
	def __contains__(self, key: T_Key) -> bool: ...
	def keys(self) -> Iterator[T_Key]: ...
	def values(self) -> Iterator[T_Value]: ...
	def items(self) -> Iterator[tuple[T_Key, T_Value]]: ...
	def pop(self, key: T_Key) -> T_Value: ...
	# XXX 本来はdefaultsが存在する場合としない場合でシグネチャーが変化するoverloadの様なメソッド
	def get(self, key: T_Key, defaults: T_Value | None = None) -> T_Value: ...


@__actual__('tuple')
class Tuple:
	"""
	Note:
		XXX 本来の定義: `class Tuple(Sequence(tuple[*T_tuple])):`
		XXX 実装にはTypeVarTupleとUnpackが必要だが、無くても問題ないため一旦対応は保留
	"""


@__actual__('None')
class Null:
	# comparison
	def __eq__(self, other: Any) -> bool: ...
	def __not__(self, other: Any) -> bool: ...

# Class

@__actual__('object')
class Object:
	def __init__(self) -> None: ...
	@property
	def __class__(self: T) -> type[T]: ...
	@property
	def __module__(self) -> str: ...
	@property
	def __dict__(self) -> dict[str, Any]: ...
	@property
	def __name__(self) -> str:
		"""Note: FIXME 本来はtypeで実装するのが正。修正を検討"""
		...

	def mro(self) -> list[type]: ...
	def __getattribute__(self, name: str) -> Any: ...
	def __setattr__(self, name: str, value: Any) -> None: ...


@__actual__('type')
class Type(Generic[T]):
	# comparison
	def __eq__(self, other: type) -> bool: ...
	def __not__(self, other: type) -> bool: ...


@__actual__('property')
class Property: ...
@__actual__('classmethod')
class ClassMethod: ...


class Exception:
	def __init__(self, *args: Any) -> None: ...

# Function

@__actual__('super')
def super_call() -> Any: ...
def id(instance: Any) -> int: ...
def print(*args: Any) -> None: ...
def reversed(seq: Sequence[T_Value]) -> Iterator[T_Value]: ...
def enumerate(iterable: Sequence[T_Value]) -> Iterator[tuple[int, T_Value]]: ...
def range(size: int) -> Iterator[int]: ...
def len(iterable: Sequence[Any]) -> int: ...
def isinstance(obj: object, class_or_tuple: type | tuple) -> bool: ...
def issubclass(_type: type, class_or_tuple: type | tuple) -> bool: ...
def open(filepath: str, mode: str = 'r', encoding: str | None = None) -> IO: ...
def getattr(obj: object, name: str) -> Any: ...
def setattr(obj: object, name: str, value: Any) -> None: ...

# Var

__file__: str = ''
__name__: str = ''
