class Any: ...
class Callable: ...
class Generic: ...
class Sequence: ...
class TypeAlias: ...
class TypeVar: ...

# FIXME 警告は一旦無視(循環参照を解決できないため)
T_Value = TypeVar('T_Value')


class Iterator(Generic[T_Value]):
	def __next__(self) -> T_Value: ...
