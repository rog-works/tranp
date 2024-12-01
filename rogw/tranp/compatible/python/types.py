from collections.abc import Callable
from typing import TypeAlias

# XXX 名前解決のためだけに存在
class Union: ...
class Unknown: ...


Standards: TypeAlias = int | float | str | bool | tuple | list | dict | type | Callable | Union | Unknown
