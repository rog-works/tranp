from typing import Any, Iterator, Sequence


@__alias__('int')
class Integer: ...


@__alias__('float')
class Float: ...


@__alias__('str')
class String: ...


@__alias__('bool')
class Boolean: ...


@__alias__('tuple')
class Tuple: ...


@__alias__('pair_')
class Pair: ...


@__alias__('list')
class List: ...


@__alias__('dict')
class Dict: ...


class Union: ...


@__alias__('None')
class Null: ...


class Unknown: ...


@__alias__('super')
class Super: ...


def id(instance: Any) -> int: ...
# def print(*args: Any) -> None: ... FIXME *argsに対応
def enumerate(iterable: Sequence[Any]) -> Iterator[tuple[int, Any]]: ...  # XXX (Sequence[T]) -> Iterator[tuple[int, T]]
def range(size: int) -> Iterator[int]: ...
def len(iterable: Sequence[Any]) -> int: ...
