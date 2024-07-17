from typing import IO, Any


def safe_load(stream: IO) -> list[str] | dict[str, Any] | None: ...
