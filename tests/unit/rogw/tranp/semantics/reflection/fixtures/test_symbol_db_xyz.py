class A:
	nx: int = 0


class B:
	ny: int = 0
	x: A = A()
	AA: type[A] = A


class C(B):
	nz: int = 0


S = ''
