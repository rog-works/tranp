from typing import Generic, TypeAlias, TypeVar, cast

from rogw.tranp.compatible.cpp.enum import CEnum
from tests.unit.rogw.tranp.semantics.reflection.fixtures.test_symbol_db_xyz import Z

DSI: TypeAlias = dict[str, int]
DSI2: TypeAlias = dict[str, DSI]
Z2: TypeAlias = Z


value: int = 0


class Base(Z):
	def __init__(self) -> None:
		self.base_str: str = ''
		# comment


class Sub(Base):
	class C:
		value: str = ''

		@classmethod
		def class_func(cls) -> dict[str, int]:
			return {cls.value: value}

	def __init__(self) -> None:
		super().__init__()
		self.numbers: list[int] = []

	@property
	def first_number(self) -> int:
		return self.numbers[0]

	def local_ref(self) -> None:
		value = False
		print(value)

	def member_ref(self) -> None:
		print(self.numbers)
		print(self.first_number)

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
					t = 0
				except Exception as e:
					t = 1
					raise e
			t = 2

		def closure() -> list[int]:
			b = [1]
			return b

		if a == 1:
			c = 0
		elif a == 2:
			c = 1
		else:
			c = 2
		c = 3

		return closure()[0]

	def assign_with_param(self, a: int) -> None:
		a1 = a + 1
		a = a1 + 1

	def relay_access(self) -> None:
		ddb = {1: {1: Base()}}
		s = ddb[1][1].base_str

	def fill_list(self, n: int) -> None:
		n_x3 = [n] * 3

	def param_default(self, d: DSI = {}) -> int:
		n = self.param_default() + 1
		n2 = self.param_default({'a': 1}) + 1
		keys = list(d.keys())
		return d['a']

	def Base(self) -> Base:
		...


class CalcOps:
	def unary(self) -> None:
		n = 1
		n_neg = -n
		n_not = not n

	def binary(self) -> None:
		n = 1 + 1
		nb0 = 1 + True
		nb1 = True + 1
		fn0 = 1 + 1.0
		fn1 = 1.0 + 1
		fn2 = 1.0 + 1.0
		fb0 = 1.0 + True
		fb1 = True + 1.0
		result = 1 + n * fn0 - fb0 / 2
		l_in = 1 in [1]
		l_not_in = 1 not in [1]
		n_is = 1 is 1
		n_is_not = 1 is not 1

	def tenary(self) -> None:
		n = 1 if 2 else 3
		s = 'a' if True else 'b'
		s_or_null = 'a' if n else None
		# エラーケース
		n_or_s = 1 if n else 'a'


class AliasOps:
	def func(self, z2: Z2) -> None:
		d: DSI = {'s': value}
		d_in_v = d['s']

		d2: DSI2 = {'s2': d}
		d2_in_dsi = d2['s']
		d2_in_dsi_in_v = d2['s2']['s']

		z2_in_x = z2.x
		new_z2_in_x = Z2().x


class TupleOps:
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

	def unpack_assign(self) -> None:
		# XXX Pythonのシンタックス上は不正
		a, b = {'a': 1}


class CompOps:
	def list_comp(self) -> None:
		values0 = [value for value in [1, 2, 3]]
		values1: list[int] = [value for value in [1, 2, 3]]
		values2 = [value for value in values0]
		strs = [str(value) for value in [1, 2, 3]]
		value = values0[0]
		value += [value for value in [0.1, 0.2]][0]

	def dict_comp(self) -> None:
		kvs0 = {key: index for index, key in enumerate(['a', 'b', 'c'])}
		kvs1: dict[str, int] = {key: index for index, key in enumerate(['a', 'b', 'c'])}
		kvs2 = {key: index for key, index in kvs0.items()}


class EnumOps:
	class Values(CEnum):
		A = 0
		B = 1

	@classmethod
	def cls_assign(cls) -> None:
		a = cls.Values.A
		d = {
			cls.Values.A: 'A',
			cls.Values.B: 'B',
		}
		da = d[cls.Values.A]

	def assign(self) -> None:
		a = EnumOps.Values.A
		d = {
			EnumOps.Values.A: 'A',
			EnumOps.Values.B: 'B',
		}
		da = d[EnumOps.Values.A]

	def cast(self) -> None:
		e = EnumOps.Values(0)
		n = int(EnumOps.Values.A)


class Nullable:
	def params(self, base: Base | None) -> None: ...
	def returns(self) -> Base | None: ...
	def var_move(self, base: Base) -> str:
		base_or_null: Base | None = None
		base_or_null = None
		base_or_null = base
		if base_or_null:
			return base_or_null.base_str

		raise Exception()

	def accessible(self, sub: Sub | None, subs: list[Sub] | None) -> None:
		s = sub.base_str if sub else ''
		n = sub.first_number if sub else 0
		# エラーケース
		arr = subs[0] if subs else []


T = TypeVar('T')

class GenericOps(Generic[T]):
	def __init__(self) -> None: ...

	def temporal(self, value: T) -> None:
		a = value

	def new(self) -> None:
		a = GenericOps[int]()

	def cast(self, sub: 'GenericOps[Sub]') -> None:
		b = cast(GenericOps[Base], sub)
