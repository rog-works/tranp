from enum import Enum


class E0(Enum):
	A = 1
	B = A + 1


class E1(Enum):
	A = E0.B.value + 1
	B = A + E0.B.value + 1

E0.A.value
E0.B.value
E1.A.value
E1.B.value
