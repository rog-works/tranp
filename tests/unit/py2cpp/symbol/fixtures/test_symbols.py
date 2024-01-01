from tests.unit.py2cpp.symbol.fixtures.test_db_xyz import Z

v: int = 0

class A(Z):
	def __init__(self) -> None:
		self.s: str = ''

class B(A):
	class B2:
		v: str = ''

	def __init__(self) -> None:
		super().__init__()
		self.v: list[int] = []

	def func1(self, b: 'list[B]') -> str:
		v = False
		print(v)
		print(self.v)
		print(b[0].v)
		B.B2.v = 'b.b2.v'
		self.x.nx = 2
		return self.s
