from enum import Enum


class E0(Enum):
	A = 1
	B = A + 1


class E1(Enum):
	A = E0.B.value + 1
	B = A + E0.B.value + 1
	C = int('1') + int('2')
	D = float('1.1') + float(1)
	E = str(0) + '.' + str(1)


E0.A.value
E0.B.value
E1.A.value
E1.B.value
E1.C.value
E1.D.value
E1.E.value
