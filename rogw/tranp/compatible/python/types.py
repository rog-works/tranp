from types import UnionType
from typing import TypeAlias

from rogw.tranp.compatible.libralies.classes import Pair, Unknown

Standards: TypeAlias = int | float | str | bool | tuple | list | dict | UnionType | Pair | Unknown
