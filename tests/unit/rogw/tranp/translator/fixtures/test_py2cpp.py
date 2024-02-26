from typing import Generic, TypeAlias, TypeVar

from rogw.tranp.compatible.cpp.enum import CEnum
from rogw.tranp.compatible.cpp.object import CP, CRef, CSP
from rogw.tranp.compatible.cpp.preprocess import directive
from rogw.tranp.compatible.python.embed import __alias__

directive('#pragma once')

T = TypeVar('T')
T2 = TypeVar('T2')

DSI: TypeAlias = dict[str, int]

class Base:
	class_base_n: int = 0

	def __init__(self, n: int) -> None:
		self.base_n: int = n

	def call(self) -> None: ...
	def __eq__(self, other: Base | bool) -> bool: ...  # FIXME Anyの実装
	def __not__(self, other: Base | bool) -> bool: ...  # FIXME Anyの実装
	def __add__(self, other: Base) -> Base: ...
	def __sub__(self, other: Base) -> Base: ...
	def __mul__(self, other: Base) -> Base: ...
	def __truediv__(self, other: Base) -> Base: ...
	def __neg__(self) -> Base: ...

class DeclOps:
	class_bp: CP[Base] | None = None
	class_map: dict[str, dict[str, list[int]]] = {'a': {'b': [1]}}

	def __init__(self) -> None:
		self.inst_var: CP[Base] | None = None

class CVarOps:
	def ret_raw(self) -> Base:
		return Base(0)

	def ret_cp(self) -> CP[Base]:
		return CP.new(Base(0))

	def ret_csp(self) -> CSP[Base]:
		return CSP.new(Base(0))

	def local_move(self) -> None:
		a: Base = Base(0)
		ap: CP[Base] = CP(a)
		asp: CSP[Base] = CSP.new(Base(0))
		ar: CRef[Base] = CRef(a)
		if True:
			a = a
			a = ap.raw()
			a = asp.raw()
			a = ar.raw()
		if True:
			ap = CP(a)
			ap = ap
			ap = asp.addr()
			ap = ar.addr()
		if True:
			# asp = a  # 構文的にNG
			# asp = ap  # 構文的にNG
			asp = asp
			# asp = ar  # 構文的にNG
		if True:
			ar = CRef(a)  # C++ではNG
			ar = ap.ref()  # C++ではNG
			ar = asp.ref()  # C++ではNG
			ar = ar  # C++ではNG

	def param_move(self, a: Base, ap: CP[Base], asp: CSP[Base], ar: CRef[Base]) -> None:
		a1 = a
		a2: Base = ap.raw()
		a3: Base = asp.raw()
		a4: Base = ar.raw()
		a = a1
		ap = CP(a2)
		# asp = a3  # 構文的にNG
		ar = CRef(a4)  # C++ではNG

	def invoke_method(self, a: Base, ap: CP[Base], asp: CSP[Base]) -> None:
		# self.invoke_method(a, CP(a), a)  # 構文的にNG
		# self.invoke_method(ap.raw(), ap, ap)  # 構文的にNG
		self.invoke_method(asp.raw(), asp.addr(), asp)

	def unary_calc(self, a: Base, ap: CP[Base], asp: CSP[Base], ar: CRef[Base]) -> None:
		neg_a = -a
		neg_a2 = -ap.raw()
		neg_a3 = -asp.raw()
		neg_a4 = -ar.raw()

	def binary_calc(self, a: Base, ap: CP[Base], asp: CSP[Base], ar: CRef[Base]) -> None:
		add = a + ap.raw() + asp.raw() + ar.raw()
		sub = a - ap.raw() - asp.raw() - ar.raw()
		mul = a * ap.raw() * asp.raw() * ar.raw()
		div = a / ap.raw() / asp.raw() / ar.raw()
		calc = a + ap.raw() * asp.raw() - ar.raw() / a
		is_a = a is ap.raw() is asp.raw() is ar.raw()
		is_not_a = a is not ap.raw() is not asp.raw() is not ar.raw()

	def tenary_calc(self, a: Base, ap: CP[Base], asp: CSP[Base], ar: CRef[Base]) -> None:
		a2 = a if True else Base()
		a3 = a if True else a
		ap2 = ap if True else ap
		asp2 = asp if True else asp
		ar2 = ar if True else ar
		ap_or_null = ap if True else None
		a_or_ap = a if True else ap  # エラーケース

	def declare(self) -> None:
		arr = [1]
		arr_p = CP(arr)
		arr_sp = CRef.new(arr)
		arr_r = CRef(arr)

class FuncOps:
	def print(self) -> None:
		print('message. %d, %f, %s', 1, 1.0, 'abc')

class EnumOps:
	class Values(CEnum):
		A = 0
		B = 1

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

class AccessOps(Base):
	def __init__(self) -> None:
		super().__init__(0)
		self.sub_s: str = ''

	def dot(self, a: AccessOps) -> None:
		print(a.base_n)
		print(a.sub_s)
		print(a.sub_s.split)
		print(a.call())
		dda = {1: {1: a}}
		print(dda[1][1].sub_s)

	def arrow(self, ap: CP[AccessOps], asp: CSP[AccessOps], arr_p: CP[list[int]]) -> None:
		print(self.base_n)
		print(self.sub_s)
		print(self.call())
		print(ap.on().base_n)
		print(ap.on().sub_s)
		print(ap.on().call())
		print(asp.on().base_n)
		print(asp.on().sub_s)
		print(asp.on().call())

	def double_colon(self) -> None:
		super().call()
		print(Base.class_base_n)
		print(AccessOps.class_base_n)
		print(EnumOps.Values.A)
		d: dict[EnumOps.Values, str] = {
			EnumOps.Values.A: 'A',
			EnumOps.Values.B: 'B',
		}

	def indexer(self, arr_p: CP[list[int]], arr_sp: CSP[list[int]], arr_ar: CRef[list[int]]) -> None:
		print(arr_p.on()[0])
		print(arr_sp.on()[0])
		print(arr_ar.on()[0])

@__alias__('Alias2')
class Alias:
	@__alias__('Inner2')
	class Inner: ...

	def __init__(self) -> None:
		self.inner: Alias.Inner = Alias.Inner()

	def in_param_return(self, a: 'Alias') -> 'Alias': ...
	def in_param_return2(self, i: 'Alias.Inner') -> 'Alias.Inner': ...

	def in_local(self) -> None:
		a = Alias()
		i = Alias.Inner()

class CompOps:
	class C:
		...

	def list_comp(self) -> None:
		values0 = [1, 2, 3]
		values1 = [value for value in values0]

	def dict_comp(self) -> None:
		kvs0 = {'a': CompOps.C()}
		kvs1 = {key: value for key, value in kvs0.items()}

class ForOps:
	def range(self) -> None:
		for i in range(10): ...

	def enumerate(self) -> None:
		keys = ['a', 'b']
		for index, key in enumerate(keys): ...

	def dict_items(self) -> None:
		kvs = {'a': 1}
		for key, value in kvs.items(): ...

class ListOps:
	def len(self) -> None:
		values = [1, 2]
		size_values = len(values)

	def pop(self) -> None:
		values = [1, 2]
		value0 = values.pop(1)
		value1 = values.pop()

	def contains(self) -> None:
		values = [1]
		b_in = 1 in values
		b_not_in = 1 not in values

	def fill(self, n: int) -> None:
		n_x3 = [n] * 3

class DictOps:
	def len(self) -> None:
		kvs = {'a': 1}
		size_kvs = len(kvs)

	def pop(self) -> None:
		values = {'a': 1, 'b': 2}
		value0 = values.pop('a')
		value1 = values.pop('b')

	def keys(self) -> None:
		kvs = {'a': 1}
		keys = list(kvs.keys())

	def values(self) -> None:
		kvs = {'a': 1}
		values = list(kvs.values())

	def decl(self) -> None:
		d = {1: [1, 2, 3]}

	def contains(self) -> None:
		d = {'a': 1}
		b_in = 'a' in d
		b_not_in = 'a' not in d

class CastOps:
	def cast_binary(self) -> None:
		f_to_n = int(1.0)
		n_to_f = float(1)
		n_to_b = bool(1)
		e_to_n = int(EnumOps.Values.A)

	def cast_string(self) -> None:
		n_to_s = str(1)
		f_to_s = str(1.0)
		s_to_n = int(n_to_s)
		s_to_f = float(f_to_s)

class Nullable:
	def params(self, p: CP[Base] | None) -> None: ...
	def returns(self) -> CP[Base] | None: ...
	def invlid_params(self, base: Base | None) -> None: ...  # エラーケース
	def invlid_returns(self) -> Base | None: ...  # エラーケース
	def var_move(self, base: Base, sp: CSP[Base]) -> Base:
		p: CP[Base] | None = None
		p = CP(base)
		p = None
		p = sp.addr()
		if p:
			return p.raw()

		raise Exception()

class Template(Generic[T]):
	class T2Class(Generic[T2]): ...

	def __init__(self, v: T) -> None: ...
	@classmethod
	def class_method_t(cls, v2: T2) -> T2: ...
	@classmethod
	def class_method_t_and_class_t(cls, v: T, v2: T2) -> T2: ...
	def method_t(self, v2: T2) -> T2: ...
	def method_t_and_class_t(self, v: T, v2: T2) -> T2: ...

def template_func(v: T) -> T: ...
