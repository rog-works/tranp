from py2cpp.cpp.directive import pragma

pragma('once')

v: int = 0

class A:
	class B:
		v: str = ''

	def __init__(self) -> None:
		self.v: list[int] = []

	def func1(self, b: 'list[int]') -> str:
		v: bool = False
		print(v)
		print(self.v)
		print(b.v)
		return A.B.v
