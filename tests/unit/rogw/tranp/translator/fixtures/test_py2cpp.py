from typing import Generic, TypeAlias, TypeVar

from rogw.tranp.compatible.cpp.enum import CEnum
from rogw.tranp.compatible.cpp.object import CObject, CP, CRef, CSP
from rogw.tranp.compatible.cpp.preprocess import directive
from rogw.tranp.compatible.python.embed import __alias__

directive('#pragma once')

T = TypeVar('T')
T2 = TypeVar('T2')

DSI: TypeAlias = dict[str, int]

class Base(CObject):
	class_base_n: int = 0

	def __init__(self, n: int = 0) -> None:
		self.base_n: int = n

	def call(self) -> None: ...
	def __add__(self, other: Base) -> Base: ...
	def __sub__(self, other: Base) -> Base: ...
	def __mul__(self, other: Base) -> Base: ...
	def __truediv__(self, other: Base) -> Base: ...
	def __neg__(self) -> Base: ...

class DeclOps:
	class_bp: Base[CP] | None = None
	class_map: dict[str, dict[str, list[int]]] = {'a': {'b': [1]}}

	def __init__(self) -> None:
		self.inst_var: Base[CP] | None = None

class CVarOps:
	def ret_raw(self) -> Base:
		return Base()

	def ret_cp(self) -> Base[CP]:
		return Base()

	def ret_csp(self) -> Base[CSP]:
		return Base()

	def local_move(self) -> None:
		a: Base = Base()
		ap: Base[CP] = a
		asp: Base[CSP] = Base()
		ar: Base[CRef] = a
		if True:
			a = a
			a = ap
			a = asp
			a = ar
		if True:
			ap = a
			ap = ap
			ap = asp
			ap = ar
		if True:
			asp = a  # エラーケース
			asp = ap  # エラーケース
			asp = asp
			asp = ar  # エラーケース
		if True:
			ar = a  # エラーケース
			ar = ap  # エラーケース
			ar = asp  # エラーケース
			ar = ar  # エラーケース

	def param_move(self, a: Base, ap: Base[CP], asp: Base[CSP], ar: Base[CRef]) -> None:
		a1 = a
		a2: Base = ap
		a3: Base = asp
		a4: Base = ar
		a = a1
		ap = a2
		asp = a3  # エラーケース
		ar = a4  # エラーケース

	def invoke_method(self, a: Base, ap: Base[CP], asp: Base[CSP]) -> None:
		self.invoke_method(a, a, a)
		self.invoke_method(ap, ap, ap)  # エラーケース
		self.invoke_method(asp, asp, asp)  # エラーケース

	def unary_calc(self, a: Base, ap: Base[CP]) -> None:
		neg_a = -a
		neg_a2 = -ap

	def binary_calc(self, a: Base, ap: Base[CP]) -> None:
		add = a + ap
		sub = a - ap
		mul = a * ap
		div = a / ap
		calc = a + ap * a - ap / a

	def tenary_calc(self, a: Base, ap: Base[CP]) -> None:
		a2 = a if True else Base()
		ap_or_null = ap if True else None  # エラーケース
		a_or_ap = a if True else ap  # エラーケース

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

class AccessOps(Base):
	def __init__(self) -> None:
		super().__init__(0)
		self.sub_s: str = ''

	def dot(self, a: AccessOps) -> None:
		print(a.base_n)
		print(a.sub_s)
		print(a.call())

	def arrow(self, ap: AccessOps[CP], asp: AccessOps[CSP]) -> None:
		print(self.base_n)
		print(self.sub_s)
		print(self.call())
		print(ap.base_n)
		print(ap.sub_s)
		print(ap.call())
		print(asp.base_n)
		print(asp.sub_s)
		print(asp.call())

	def double_colon(self) -> None:
		super().call()
		print(Base.class_base_n)
		print(AccessOps.class_base_n)
		print(EnumOps.Values.A)
		d: dict[EnumOps.Values, str] = {
			EnumOps.Values.A: 'A',
			EnumOps.Values.B: 'B',
		}

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
	def params(self, p: Base[CP] | None) -> None: ...
	def returns(self) -> Base[CP] | None: ...
	def invlid_params(self, base: Base | None) -> None: ...  # エラーケース
	def invlid_returns(self) -> Base | None: ...  # エラーケース
	def var_move(self, base: Base, sp: Base[CSP]) -> Base:
		p: Base[CP] | None = None
		p = base
		p = sp
		p = None
		if p:
			return p

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
