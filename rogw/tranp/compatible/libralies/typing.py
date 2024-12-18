class Annotated: ...
class Any: ...
class ClassVar: ...
class ForwardRef: ...
class Generic: ...
class IO: ...
class NamedTuple: ...
class Protocol: ...
class TypeAlias: ...
class TypeVar: ...
class TypeVarTuple: ...
class Union: ...


# FIXME 警告は一旦無視(循環参照を解決できないため)
T = TypeVar('T')
Self = TypeVar('Self')


class ParamSpec:
	# XXX ParamSpecArgs/ParamSpecKwargsへの変更を検討
	class args: ...
	class kwargs: ...


def override(decorated: T) -> T: ...
def cast(to: type[T], value: Any) -> T: ...
def get_origin(t: Any) -> Any: ...
