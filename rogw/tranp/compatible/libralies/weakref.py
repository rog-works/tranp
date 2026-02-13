from collections.abc import Callable
from typing import Generic, TypeVar

T = TypeVar('T')


class ReferenceType(Generic[T]): ...


def finalize(obj: object, callback: Callable[[], None]) -> None: ...
