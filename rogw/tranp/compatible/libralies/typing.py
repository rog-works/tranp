class Any: ...
class Callable: ...
class ClassVar: ...
class IO: ...
class Generic: ...
class NamedTuple: ...
class Protocol: ...
class Sequence: ...
class TypeAlias: ...
class TypeVar: ...
class TypeVarTuple: ...
class Union: ...


# FIXME 警告は一旦無視(循環参照を解決できないため)
T = TypeVar('T')
Self = TypeVar('Self')


# FIXME castの定義のため必要。classes側の定義は消さないこと
# FIXME __actual__の未定義エラーは解決方法がないため一旦無視
@__actual__('type')
class Type(Generic[T]): ...


class Iterator(Generic[T]):
	def __next__(self) -> T: ...


class ParamSpec:
	# XXX ParamSpecArgs/ParamSpecKwargsへの変更を検討
	class args: ...
	class kwargs: ...


def cast(to: type[T], value: Any) -> T: ...
