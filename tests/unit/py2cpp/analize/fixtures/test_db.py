from tests.unit.py2cpp.analize.fixtures.test_db_xyz import Z

v: int = 0

class A(Z):
	def __init__(self) -> None:
		self.s: str = ''

class B(A):
	class B2:
		v: str = ''

		@classmethod
		def class_func(cls) -> dict[str, int]:
			return {cls.v: v}

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

	def func2(self) -> int:
		def closure() -> int:
			a = self.v[0]
			return a

		for i in range(10):
			print(v)
			if i == 1:
				return closure()

		try:
			while True:
				if v == 1:
					break
		except Exception as e:
			raise e

		return closure()
