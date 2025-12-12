from enum import Enum


class A:
	class E(Enum):
		A = 1
		B = 2

	def method(self) -> None:
		if True: ...
		if False: ...

	def method2(self) -> None:
		...


def func() -> None:
	...
