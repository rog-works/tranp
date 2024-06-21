from abc import ABCMeta, abstractmethod
from typing import Generic, TypeAlias, TypeVar, cast

from rogw.tranp.compatible.cpp.embed import __allow_override__, __embed__, __struct__
from rogw.tranp.compatible.cpp.enum import CEnum
from rogw.tranp.compatible.cpp.object import CP, CRawConst, CRef, CSP
from rogw.tranp.compatible.cpp.preprocess import c_include, c_macro, c_pragma

c_pragma('once')
c_include('<memory>')
c_macro('MACRO()')

T = TypeVar('T')
T2 = TypeVar('T2')

DSI: TypeAlias = dict[str, int]


class Base(metaclass=ABCMeta):
	@abstractmethod
	def sub_implements(self) -> None: ...

	@__allow_override__
	def allowed_overrides(self) -> int:
		return 1


class Sub(Base):
	class_base_n: int = 0

	def __init__(self, n: int) -> None:
		self.base_n: int = n

	def sub_implements(self) -> None: ...
	def call(self) -> None: ...
	# FIXME other: Any
	def __eq__(self, other: 'Sub | bool') -> bool: ...
	# FIXME other: Any
	def __not__(self, other: 'Sub | bool') -> bool: ...
	def __add__(self, other: 'Sub') -> 'Sub': ...
	def __sub__(self, other: 'Sub') -> 'Sub': ...
	def __mul__(self, other: 'Sub') -> 'Sub': ...
	def __truediv__(self, other: 'Sub') -> 'Sub': ...
	def __neg__(self) -> 'Sub': ...


class DeclOps:
	class_bp: CP[Sub] | None = None
	class_map: dict[str, dict[str, list[int]]] = {'a': {'b': [1]}}

	def __init__(self) -> None:
		self.inst_var: CP[Sub] | None = None


class CVarOps:
	def ret_raw(self) -> Sub:
		return Sub(0)

	def ret_cp(self) -> CP[Sub]:
		return CP.new(Sub(0))

	def ret_csp(self) -> CSP[Sub]:
		return CSP.new(Sub(0))

	def local_move(self) -> None:
		a: Sub = Sub(0)
		ap: CP[Sub] = CP(a)
		asp: CSP[Sub] = CSP.new(Sub(0))
		ar: CRef[Sub] = CRef(a)
		if True:
			a = a
			a = ap.raw
			a = asp.raw
			a = ar.raw
		if True:
			ap = CP(a)
			ap = ap
			ap = asp.addr
			ap = ar.addr
		if True:
			# asp = a  # 構文的にNG
			# asp = ap  # 構文的にNG
			asp = asp
			# asp = ar  # 構文的にNG
		if True:
			# C++ではNG
			ar = CRef(a)
			# C++ではNG
			ar = ap.ref
			# C++ではNG
			ar = asp.ref
			# C++ではNG
			ar = ar

	def param_move(self, a: Sub, ap: CP[Sub], asp: CSP[Sub], ar: CRef[Sub]) -> None:
		a1 = a
		a2: Sub = ap.raw
		a3: Sub = asp.raw
		a4: Sub = ar.raw
		a = a1
		ap = CP(a2)
		# asp = a3  # 構文的にNG
		# C++ではNG
		ar = CRef(a4)

	def invoke_method(self, a: Sub, ap: CP[Sub], asp: CSP[Sub]) -> None:
		# self.invoke_method(a, CP(a), a)  # 構文的にNG
		# self.invoke_method(ap.raw, ap, ap)  # 構文的にNG
		self.invoke_method(asp.raw, asp.addr, asp)

	def unary_calc(self, a: Sub, ap: CP[Sub], asp: CSP[Sub], ar: CRef[Sub]) -> None:
		neg_a = -a
		neg_a2 = -ap.raw
		neg_a3 = -asp.raw
		neg_a4 = -ar.raw

	def binary_calc(self, a: Sub, ap: CP[Sub], asp: CSP[Sub], ar: CRef[Sub]) -> None:
		add = a + ap.raw + asp.raw + ar.raw
		sub = a - ap.raw - asp.raw - ar.raw
		mul = a * ap.raw * asp.raw * ar.raw
		div = a / ap.raw / asp.raw / ar.raw
		calc = a + ap.raw * asp.raw - ar.raw / a
		is_a = a is ap.raw is asp.raw is ar.raw
		is_not_a = a is not ap.raw is not asp.raw is not ar.raw

	def tenary_calc(self, a: Sub, ap: CP[Sub], asp: CSP[Sub], ar: CRef[Sub]) -> None:
		a2 = a if True else Sub()
		a3 = a if True else a
		ap2 = ap if True else ap
		asp2 = asp if True else asp
		ar2 = ar if True else ar
		ap_or_null = ap if True else None
		# エラーケース
		a_or_ap = a if True else ap

	def declare(self) -> None:
		arr = [1]
		arr_p = CP(arr)
		arr_sp = CSP.new([1])
		arr_r = CRef(arr)

	def default_param(self, ap: CP[Sub] | None = None) -> int:
		n = ap.on.base_n if ap else 0
		n2 = self.default_param()
		return n

	def const_move(self, a: Sub, ap: CP[Sub], asp: CSP[Sub], r: CRef[Sub]) -> None:
		a_const0 = CRawConst(a)
		a0 = a_const0.raw
		r0_const = a_const0.ref
		ap0_const = a_const0.addr

		ap_const1 = ap.const
		a1 = ap_const1.raw
		r_const1 = ap_const1.ref

		asp_const2 = asp.const
		a2 = asp_const2.raw
		r_const2 = asp_const2.ref
		ap_const2 = asp_const2.addr

		r_const3 = r.const
		a3 = r_const3.raw
		ap_const3 = r_const3.addr


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


class AccessOps(Sub):
	def __init__(self) -> None:
		super().__init__(0)
		self.sub_s: str = ''

	def dot(self, a: 'AccessOps') -> None:
		print(a.base_n)
		print(a.sub_s)
		print(a.sub_s.split)
		print(a.call())
		dda = {1: {1: a}}
		print(dda[1][1].sub_s)

	def arrow(self, ap: 'CP[AccessOps]', asp: 'CSP[AccessOps]', arr_p: CP[list[int]]) -> None:
		print(self.base_n)
		print(self.sub_s)
		print(self.call())
		print(ap.on.base_n)
		print(ap.on.sub_s)
		print(ap.on.call())
		print(asp.on.base_n)
		print(asp.on.sub_s)
		print(asp.on.call())

	def double_colon(self) -> None:
		super().call()
		print(Sub.class_base_n)
		print(AccessOps.class_base_n)
		print(EnumOps.Values.A)
		d: dict[EnumOps.Values, str] = {
			EnumOps.Values.A: 'A',
			EnumOps.Values.B: 'B',
		}

	def indexer(self, arr_p: CP[list[int]], arr_sp: CSP[list[int]], arr_ar: CRef[list[int]]) -> None:
		print(arr_p.on[0])
		print(arr_sp.on[0])
		print(arr_ar.on[0])


class Alias:
	class Values(CEnum):
		A = 1
		B = 2

	class Inner: ...

	def __init__(self) -> None:
		self.inner: Alias.Inner = Alias.Inner()

	def in_param_return(self, a: 'Alias') -> 'Alias': ...
	def in_param_return2(self, i: 'Alias.Inner') -> 'Alias.Inner': ...

	def in_local(self) -> None:
		a = Alias()
		i = Alias.Inner()

	@classmethod
	def in_class_method(cls) -> None:
		cls.in_class_method()
		a = cls.Values.A
		d = {
			cls.Values.A: cls.Values.B,
			cls.Values.B: cls.Values.A,
		}
		d2 = {
			int(cls.Values.A): [int(cls.Values.B)],
			int(cls.Values.B): [int(cls.Values.A)],
		}


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
		s_to_s = str('')

	def cast_class(self, sub: Sub, sub_p: CP[Sub]) -> None:
		b = cast(Base, sub)
		bp = cast(CP[Base], sub_p)


class Nullable:
	def params(self, p: CP[Sub] | None) -> None: ...
	def returns(self) -> CP[Sub] | None: ...
	# エラーケース
	def invlid_params(self, base: Sub | None) -> None: ...
	# エラーケース
	def invlid_returns(self) -> Sub | None: ...
	def var_move(self, base: Sub, sp: CSP[Sub]) -> Sub:
		p: CP[Sub] | None = None
		p = CP(base)
		p = None
		p = sp.addr
		if p:
			return p.raw

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


class GenericOps(Generic[T]):
	def __init__(self) -> None: ...

	def temporal(self, value: T) -> None:
		a = value

	def new(self) -> None:
		a = GenericOps[int]()


@__struct__
@__embed__('prop.a', '/** @var A */')
@__embed__('prop.b', '/** @var B */')
class Struct:
	def __init__(self, a: int, b: str) -> None:
		self.a: int = a
		self.b: str = b


def template_func(v: T) -> T: ...
