class X:
	nx: int = 0


class Y:
	ny: int = 0
	x: X = X()


class Z(Y):
	nz: int = 0
