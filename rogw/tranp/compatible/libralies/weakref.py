from collections.abc import Callable


def finalize(obj: object, callback: Callable[[], None]) -> None: ...
