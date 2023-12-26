from py2cpp.cpp.directive import pragma

pragma('once')

v: int = 0

class A:
	def __init__(self) -> None:
		self.s: str = ''

class B(A):
	class B2:
		v: str = ''

	def __init__(self) -> None:
		self.v: list[int] = []

	def func1(self, b: 'list[B]') -> str:
		v = False
		print(v)
		print(self.v)
		print(b[0].v)
		return self.s
