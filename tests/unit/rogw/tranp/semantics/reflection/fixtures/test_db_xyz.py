from typing import ClassVar, TypeAlias


class A:
	nx: ClassVar[int] = 0


class B:
	ny: ClassVar[int] = 0
	x: ClassVar[A] = A()
	AA: TypeAlias = A


class C(B):
	nz: ClassVar[int] = 0


S = ''
