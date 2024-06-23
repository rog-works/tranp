class Any: ...
class Callable: ...
class Generic: ...
class Sequence: ...
class TypeAlias: ...
class TypeVar: ...

# FIXME 警告は一旦無視(循環参照を解決できないため)
T = TypeVar('T')


# FIXME 2重定義、且つ__actual__の定義なし
@__actual__('type')
class Type(Generic[T]): ...
class Iterator(Generic[T]):
	def __next__(self) -> T: ...


def cast(to: type[T], value: Any) -> T: ...
