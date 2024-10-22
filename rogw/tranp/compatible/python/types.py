from typing import Callable, TypeAlias

from rogw.tranp.compatible.libralies.classes import Union, Unknown

Standards: TypeAlias = int | float | str | bool | tuple | list | dict | type | Callable | Union | Unknown
