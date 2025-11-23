from collections.abc import Callable
from typing import Generic, TypeVar, TypeVarTuple

T_Scalar = TypeVar('T_Scalar', bool, int, float, str)
T_Args = TypeVarTuple('T_Args')


class Payload(Generic[T_Scalar]):
	value: T_Scalar

	def __init__(self, value: T_Scalar) -> None:
		self.value = value


class Action(Generic[*T_Args]):
	def __init__(self, a: str, b: str, c: Callable[[*T_Args], None]) -> None: ...


class A(Generic[T_Scalar]):
	def __init__(self, defaults: T_Scalar) -> None:
		Action[Payload[T_Scalar]](a='a', b='b', c=lambda e: print(e.value))
