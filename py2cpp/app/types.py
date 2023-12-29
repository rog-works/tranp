from typing import Any, Callable, TypeAlias

ModuleDefinitions: TypeAlias = dict[str, str | Callable[..., Any]]
