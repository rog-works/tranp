from collections.abc import Callable
from typing import TypeAlias

# XXX 名前解決のためだけに存在
class Union: ...
class Unknown: ...


Standards: TypeAlias = bool | int | float | str | list | dict | tuple | type | Callable | Union | Unknown
