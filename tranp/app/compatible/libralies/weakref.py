from collections.abc import Callable


class ReferenceType[T]: ...


def finalize(obj: object, callback: Callable[[], None]) -> None: ...
