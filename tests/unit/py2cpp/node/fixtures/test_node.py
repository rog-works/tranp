from py2cpp.compatible.cpp.enum import CEnum

class A:
	class E(CEnum):
		A = 1
		B = 2

	def method(self) -> None:
		if True: ...
		if False: ...

	def method2(self) -> None:
		...

def func() -> None:
	...
