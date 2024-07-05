from typing import TypeAlias


class A:
	nx: int = 0


class B:
	ny: int = 0
	x: A = A()
	AA: TypeAlias = A


class C(B):
	nz: int = 0


S = ''
