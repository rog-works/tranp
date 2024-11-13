from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from typing import ClassVar, Generic, Self, TypeAlias, TypeVar, TypeVarTuple, cast

from rogw.tranp.compatible.cpp.classes import char, void
from rogw.tranp.compatible.cpp.embed import Embed
from rogw.tranp.compatible.cpp.enum import CEnum as Enum
from rogw.tranp.compatible.cpp.object import CP, CPConst, CRawConst, CRef, CSP, CRefConst, c_func_ref
from rogw.tranp.compatible.cpp.preprocess import c_include, c_macro, c_pragma

c_pragma('once')
c_include('<memory>')
c_macro('MACRO()')

T = TypeVar('T')
T2 = TypeVar('T2')

DSI: TypeAlias = dict[str, int]
TSII: TypeAlias = tuple[str, int, int]


class Base(metaclass=ABCMeta):
	@abstractmethod
	def sub_implements(self) -> None: ...

	@Embed.allow_override
	def allowed_overrides(self) -> int:
		return 1

	@classmethod
	def base_class_func(cls) -> int: ...

	@property
	def base_prop(self) -> str: ...

	@Embed.public
	@Embed.pure
	def _pure_public_method(self) -> str: ...


class Sub(Base):
	class_base_n: ClassVar['int'] = 0
	base_n: int

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
	class_bp: ClassVar[CP[Sub] | None] = None
	class_map: ClassVar[dict[str, dict[str, list[CP[int]]]]] = {'a': {'b': []}}
	inst_var0: CP[Sub] | None
	inst_var1: Sub
	inst_arr: list[CP[int]]
	inst_map: dict[str, CP[int]]
	inst_tsiis: list[TSII]

	def __init__(self) -> None:
		self.inst_var0: CP[Sub] | None = None
		self.inst_var1: Sub
		self.inst_arr: list[CP[int]] = []
		self.inst_map: dict[str, CP[int]] = {}
		self.inst_tsiis: list[TSII] = []
		n = self.prop

	@property
	def prop(self) -> int:
		return 1


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

	def binary_calc(self, a: Sub, ap: CP[Sub], asp: CSP[Sub], ar: CRef[Sub], apn: CP[Sub] | None) -> None:
		add = a + ap.raw + asp.raw + ar.raw
		sub = a - ap.raw - asp.raw - ar.raw
		mul = a * ap.raw * asp.raw * ar.raw
		div = a / ap.raw / asp.raw / ar.raw
		mod = 1.0 % 1
		calc = a + ap.raw * asp.raw - ar.raw / a
		is_a = a is ap.raw is asp.raw is ar.raw
		is_not_a = a is not ap.raw is not asp.raw is not ar.raw
		is_null = apn is None and apn is not None

	def tenary_calc(self, a: Sub, ap: CP[Sub], asp: CSP[Sub], ar: CRef[Sub]) -> None:
		a2 = a if True else Sub()
		a3 = a if True else a
		ap2 = ap if True else ap
		asp2 = asp if True else asp
		ar2 = ar if True else ar
		ap_or_null = ap if True else None

	def declare(self) -> None:
		arr = [1]
		arr_p = CP(arr)
		arr_p2 = CP.new(list[int]())
		arr_sp = CSP.new([1])
		arr_sp2 = CSP.new(list[int]())
		arr_sp3 = CSP.new(list[int]() * 2)
		arr_sp4 = CSP.new([0] * 2)
		arr_r = CRef(arr)
		n_sp_empty = CSP[int].empty()
		this_p = CP(self)
		this_ps = [CP(self)]
		this_ps_ref = CRef(this_ps)

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

	def to_void(self, a: Sub, ap: CP[Sub], asp: CSP[Sub], r: CRef[Sub]) -> None:
		a_to_vp = cast(CP[void], CP(a))
		ap_to_vp = cast(CP[void], ap)
		asp_to_vp = cast(CP[void], asp.addr)
		r_to_vp = cast(CP[void], r.addr)

	def local_decl(self, n: int) -> None:
		p_arr = [CP(n)]
		p_map = {n: CP(n)}

	def addr_calc(self, sp0: CP[Sub], sp1: CP[Sub], bp: CP[Base]) -> None:
		a = sp0 - sp1
		b = sp0 + 1

	@property
	def raw(self) -> int:
		p = CP(self)
		return p.on.raw

	@property
	def prop_relay(self) -> 'CVarOps':
		a = self.prop_relay.prop_relay
		return self


class FuncOps:
	def print(self) -> None:
		print('message. %d, %f, %s', 1, 1.0, 'abc')

	def kw_params(self, **kwargs: int) -> str:
		a = self.kw_params(a=1, b=2)
		return ''


class EnumOps:
	class Values(Enum):
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
	sub_s: str

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
		print(ap.on.base_prop)
		print(asp.on.base_n)
		print(asp.on.sub_s)
		print(asp.on.call())

	def double_colon(self) -> None:
		super().call()
		print(Sub.class_base_n)
		print(Sub.base_class_func())
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
	inner: 'Alias.Inner'

	def __init__(self) -> None:
		self.inner: Alias.Inner = Alias.Inner()

	class Values(Enum):
		A = 1
		B = 2

	class Inner:
		V: ClassVar[int] = 0

		def func(self) -> None: ...

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

	class InnerB(Inner):
		def super_call(self) -> None:
			super().func()

	def litelize(self) -> None:
		print(self.__class__.__name__)
		print(self.__module__)
		print(Alias.__module__)
		print(Alias.Inner.__name__)
		print(Alias.in_local.__name__)
		print(Alias.in_local.__qualname__)
		print(Alias.Inner.func.__qualname__)


class CompOps:
	class C:
		...

	def list_comp(self) -> None:
		values0 = [1, 2, 3]
		values1 = [value for value in values0]

	def dict_comp(self) -> None:
		kvs0_0 = {'a': CompOps.C()}
		kvs0_1 = {key: value for key, value in kvs0_0.items()}
		kvsp_0 = CP(kvs0_0)
		kvsp_1 = {key: value for key, value in kvsp_0.on.items()}
		values = [[1, 2], [3, 4]]
		kvs2 = {in_values[0]: in_values[1] for in_values in values}


class ForOps:
	def range(self) -> None:
		for i in range(10): ...

	def enumerate(self) -> None:
		keys = ['a', 'b']
		for index, key in enumerate(keys): ...

	def dict_items(self) -> None:
		kvs = {'a': 1}
		for key, value in kvs.items(): ...
		kvs_p = CP(kvs)
		for key, value in kvs_p.on.items(): ...


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

	def slice(self, ns: list[int]) -> None:
		ns0 = ns[1:]
		ns1 = ns[:5]
		ns2 = ns[3:9:2]

	def delete(self, ns: list[int]) -> None:
		del ns[1], ns[2]

	def insert(self, ns: list[int], n: int) -> None:
		ns.insert(1, n)

	def extend(self, ns0: list[int], ns1: list[int]) -> None:
		ns0.extend(ns1)

	def clear(self, arr: list[int]) -> None:
		arr.clear()


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

	def delete(self, dsn: dict[str, int]) -> None:
		del dsn['a'], dsn['b']

	def clear(self, dsn: dict[str, int]) -> None:
		dsn.clear()


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
		dssp = {'a': sub_p}
		dsbp = cast(dict[str, CP[Base]], dssp)


class Nullable:
	def params(self, p: CP[Sub] | None) -> None: ...
	def returns(self) -> CP[Sub] | None: ...
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


@Embed.struct
@Embed.meta('prop.a', '/** @var A */')
@Embed.meta('prop.b', '/** @var B */')
class Struct:
	a: int
	b: str

	def __init__(self, a: int, b: str) -> None:
		self.a: int = a
		self.b: str = b


class StringOps:
	def methods(self, s: str) -> None:
		a = s.startswith('')
		b = s.endswith('')

	def slice(self, s: str) -> None:
		a = s[1:]
		b = s[:5]

	def len(self, s: str) -> None:
		a = len(s)

	def format(self, s: str) -> None:
		a = '{n}, {f}, {b}, {s}, {sp}, {p}'.format(n=1, f=2.0, b=True, s='3', sp=s, p=CP(self))
		b = s.format(1, 2, 3)


class AssignOps:
	def assign(self, tsiis: list[TSII]) -> None:
		a: int = 1
		b = 'b'
		b += str(a)
		tsiis2 = tsiis
		tsii = tsiis[0]
		ts, ti1, ti2 = tsii


def template_func(v: T) -> T: ...


class ForFlows:
	def if_elif_else(self) -> None:
		if 1: ...
		elif 2: ...
		else: ...

	def while_only(self) -> None:
		while True: ...

	def fors(self, strs: list[str], dsn: dict[str, int], cps: list[CPConst[int]]) -> None:
		for i in range(2): ...
		for i in range(len(strs)): ...
		for index, value in enumerate([1]): ...
		for index, value in enumerate(strs): ...
		for key, value in {'a': 1}.items(): ...
		for key, value in dsn.items(): ...
		for s in strs: ...
		for value in dsn.values(): ...
		for cp in cps: ...


class ForClassMethod:
	@classmethod
	def make(cls: type[Self]) -> Self:
		inst = cls()
		return inst


class ForFuncCall:
	class CallableType:
		func: Callable[[int, str], bool]

		def __init__(self, func: Callable[[int, str], bool]) -> None:
			self.func: Callable[[int, str], bool] = func

	class Copy:
		def __py_copy__(self, origin: 'CRef[ForFuncCall.Copy]') -> None:
			...

		def move_obj(self, via: 'CRef[ForFuncCall.Copy]', to: 'CRef[ForFuncCall.Copy]') -> None:
			to.copy(via)

		def move_scalar(self, output: 'CRef[int]') -> None:
			output.copy(CRef(1))

	def move_assign(self, caller: CallableType) -> None:
		func = caller.func
		b0 = caller.func(0, '')
		b1 = func(0, '')


class ForBinaryOperator:
	def char_op_by_str(self, string: str) -> None:
		a = string[0] >= char('A')
		b = string[0] <= char('Z')
		c = char(string[0])

	def decimal_mod(self) -> None:
		print((1.0 % 1) % (1 % 1.0))


TArgs = TypeVarTuple('TArgs')


class ForTemplateClass:
	class Delegate(Generic[*TArgs]):
		def bind(self, obj: CP[T], method: CRefConst[Callable[[T, *TArgs], None]]) -> None: ...
		def invoke(self, *args: *TArgs) -> None: ...

	class A:
		def func(self, b: bool, c: int) -> None: ...

	def bind_call(self, a: CP[A]) -> None:
		d = ForTemplateClass.Delegate[bool, int]()
		d.bind(a, c_func_ref(ForTemplateClass.A.func).const)
		d.invoke(True, 1)
