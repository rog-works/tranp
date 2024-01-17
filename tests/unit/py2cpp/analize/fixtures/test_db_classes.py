from typing import Any, Iterator


@__alias__('int')
class Integer: pass


@__alias__('float')
class Float: pass


@__alias__('str')
class String: pass


@__alias__('bool')
class Boolean: pass


@__alias__('tuple')
class Tuple: pass


@__alias__('pair_')
class Pair: pass


@__alias__('list')
class List: pass


@__alias__('dict')
class Dict: pass


@__alias__('None')
class Null: pass


class Unknown: pass


@__alias__('super')
class Super: pass


def id(instance: Any) -> int: ...
# def print(*args: Any) -> None: ... FIXME *argsに対応
def enumerate(iterable: Iterator[Any]) -> Iterator[tuple[int, Any]]: ...  # XXX (Iterator[T]) -> Iterator[tuple[int, T]]
def range(size: int, step: int = 1) -> Iterator[int]: ...
def len(iterable: Iterator[Any]) -> int: ...
