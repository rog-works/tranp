from types import UnionType
from typing import TypeAlias

from rogw.tranp.compatible.python.classes import Pair, Unknown

Primitives: TypeAlias = int | float | str | bool | tuple | list | dict | UnionType | Pair | Unknown
