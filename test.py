from typing import Any, Generic, TypeVar

from rogw.tranp.compatible.cpp.enum import CEnum

T = TypeVar('T')


class E(CEnum):
	A = 1
	B = 2


class A:
	class B:
		b: bool = False

		@classmethod
		def sb_func(cls) -> bool:
			return cls.b

	@classmethod
	def new(cls) -> 'A':
		return cls()


class G(Generic[T]): ...


def Cast(t: type[T], value: Any) -> T:
	...


n = Cast(int, 1.0)
a = A.new()
b = A.B.sb_func()
c = type[int]
e = E.A
