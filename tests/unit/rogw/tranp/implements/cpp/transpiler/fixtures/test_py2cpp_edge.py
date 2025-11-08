from collections.abc import Callable
from typing import Generic, TypeVar, TypeVarTuple

T_Scalar = TypeVar('T_Scalar', bool, int, float, str)
T_Args = TypeVarTuple('T_Args')


class VDOM: ...


class Action(VDOM, Generic[*T_Args]):
	def __init__(self, event: str, scope: str, callback: Callable[[*T_Args], None]) -> None: ...


class A(VDOM, Generic[T_Scalar]):
	def __init__(self, defaults: T_Scalar) -> None:
		Action[T_Scalar](event='hoge', scope='fuga', callback=lambda e: print(e))
