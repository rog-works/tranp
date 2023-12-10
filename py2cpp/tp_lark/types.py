from typing import TypeAlias

from lark import Token, Tree


Entry: TypeAlias = Tree | Token | None
