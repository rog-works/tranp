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

	def local_ref(self) -> None:
		value = False
		print(value)

	def member_ref(self) -> None:
		print(self.numbers)

	def member_write(self) -> None:
		self.x.nx = 2
		Sub.C.value = 'update'

	def param_ref(self, param: int) -> None:
		print(param)

	def list_ref(self, subs: 'list[Sub]') -> None:
		print(self.numbers[0])
		print(subs[0].numbers)

	def base_ref(self) -> None:
		print(self.base_str)

	def returns(self) -> str:
		return self.base_str

	def invoke_method(self) -> None:
		self.invoke_method()

	def decl_with_pop(self) -> None:
		poped = self.numbers.pop()

	def decl_locals(self) -> int:
		a = 1
		if a:
			a = a + 1
			for i in range(a):
				try:
					i = 0
				except Exception as e:
					raise e

		def closure() -> list[int]:
			b = [1]
			return b

		return closure()[0]

DSI: TypeAlias = dict[str, int]
DSI2: TypeAlias = dict[str, DSI]
Z2: TypeAlias = Z

class AliasCheck:
	def func(self, z2: Z2) -> None:
		d: DSI = {'s': value}
		d_in_v = d['s']

		d2: DSI2 = {'s2': d}
		d2_in_dsi = d2['s']
		d2_in_dsi_in_v = d2['s2']['s']

		z2_in_x = z2.x
		new_z2_in_x = Z2().x
