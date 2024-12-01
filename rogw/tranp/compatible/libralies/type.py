# FIXME TypeVar/Genericは言語構造として解釈されるため存在していなくても今のところ問題はない
T = TypeVar('T')


class type(Generic[T]): ...
