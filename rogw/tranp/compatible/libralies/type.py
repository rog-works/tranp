# XXX 以下のクラス・テンプレート型はあくまでもtypeを定義するためのものであり、共有はしない点に注意
# FIXME 警告は一旦無視(循環参照を解決できないため)
class Generic: ...


T = TypeVar('T')


class type(Generic[T]): ...
