from typing import TypeAlias

from tests.unit.py2cpp.analyze.fixtures.test_db_xyz import Z

value: int = 0

class Base(Z):
	def __init__(self) -> None:
		self.base_str: str = ''

class Sub(Base):
	class C:
		value: str = ''

		@classmethod
		def class_func(cls) -> dict[str, int]:
			return {cls.value: value}

	def __init__(self) -> None:
		super().__init__()
		self.numbers: list[int] = []

	def func1(self, subs: 'list[Sub]') -> str:
		value = False
		print(value)
		print(self.numbers)
		print(subs[0].numbers)
		Sub.C.value = 'b.b2.v'
		self.x.nx = 2
		v2 = self.numbers.pop()
		print(self.func3()[0].numbers)
		return self.base_str

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
			b = self.numbers
			return b

		return closure()[0]

	def func3(self) -> 'list[Sub]':
		...

DSI: TypeAlias = dict[str, int]
DSI2: TypeAlias = dict[str, DSI]
Z2: TypeAlias = Z

def func(z2: Z2) -> None:
	d: DSI = {'s': value}
	d_in_v = d['s']

	d2: DSI2 = {'s2': d}
	d2_in_dsi = d2['s']
	d2_in_dsi_in_v = d2['s2']['s']

	z2_in_x = z2.x
	new_z2_in_x = Z2().x
