from typing import TypeAlias

from tests.unit.py2cpp.analyze.fixtures.test_db_xyz import Z

v: int = 0

class Base(Z):
	def __init__(self) -> None:
		self.s: str = ''

class Sub(Base):
	class B2:
		v: str = ''

		@classmethod
		def class_func(cls) -> dict[str, int]:
			return {cls.v: v}

	def __init__(self) -> None:
		super().__init__()
		self.v: list[int] = []

	def func1(self, b: 'list[Sub]') -> str:
		v = False
		print(v)
		print(self.v)
		print(b[0].v)
		Sub.B2.v = 'b.b2.v'
		self.x.nx = 2
		v2 = self.v.pop()
		print(self.func3()[0].v)
		return self.s

	def func2(self) -> int:
		a = 1
		if a:
			a = a + 1
			for i in range(a):
				try:
					i = 0
				except Exception as e:
					raise e

		def closure() -> list[int]:
			b = self.v
			return b

		return closure()[0]

	def func3(self) -> 'list[Sub]':
		...

DSI: TypeAlias = dict[str, int]
DSI2: TypeAlias = dict[str, DSI]
Z2: TypeAlias = Z

def func(z2: Z2) -> None:
	d: DSI = {'s': v}
	d_in_v = d['s']

	d2: DSI2 = {'s2': d}
	d2_in_dsi = d2['s']
	d2_in_dsi_in_v = d2['s2']['s']

	z2_in_x = z2.x
	new_z2_in_x = Z2().x
