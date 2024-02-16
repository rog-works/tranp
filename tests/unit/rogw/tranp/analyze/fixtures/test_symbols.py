from typing import TypeAlias

from tests.unit.rogw.tranp.analyze.fixtures.test_db_xyz import Z

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

class Ops:
	def sum(self) -> None:
		n = 1 + 1
		nb0 = 1 + True
		nb1 = True + 1
		fn0 = 1 + 1.0
		fn1 = 1.0 + 1
		fn2 = 1.0 + 1.0
		fb0 = 1.0 + True
		fb1 = True + 1.0

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

class TupleCheck:
	def unpack(self) -> None:
		for key0, value0 in {'a': 1}.items(): ...
		for value1 in {'a': 1}.values(): ...
		for key1 in {'a': 1}.keys(): ...
		for pair0 in {'a': 1}: ...

		d: DSI2 = {'a': {'b': 2}}
		for key10, value10 in d.items(): ...
		for value11 in d.values(): ...
		for key11 in d.keys(): ...
		for pair10 in d: ...
