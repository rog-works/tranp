from typing import Generic

from rogw.tranp.compatible.python.template import T, T_Key, T_Value


class Callable: ...
class Sequence: ...
# XXX ItemsView用の定義。実際は存在しない点に注意
class Pair(Generic[T_Key, T_Value]): ...


class Iterator(Generic[T]):
	def __next__(self) -> T: ...


class ItemsView(Generic[T_Key, T_Value]):
	def __next__(self) -> Iterator[Pair[T_Key, T_Value]]: ...
