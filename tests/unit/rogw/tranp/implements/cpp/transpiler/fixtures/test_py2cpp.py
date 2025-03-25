from abc import ABCMeta, abstractmethod
from collections.abc import Callable
from typing import Annotated, ClassVar, Generic, Protocol, Self, TypeAlias, TypeVar, TypeVarTuple, cast

from rogw.tranp.compatible.cpp.classes import char, void
from rogw.tranp.compatible.cpp.enum import CEnum as Enum
from rogw.tranp.compatible.cpp.object import CP, CPConst, CRawConst, CRef, CSP, CRefConst, c_func_invoke, c_func_ref
from rogw.tranp.compatible.cpp.preprocess import c_include, c_macro, c_pragma
from rogw.tranp.compatible.python.embed import Embed

c_pragma('once')
c_include('<memory>')
c_macro('MACRO()')

T = TypeVar('T')
T2 = TypeVar('T2')

DSI: TypeAlias = dict[str, int]
TSII: TypeAlias = tuple[str, int, int]


class Values(Enum):
	A = 0
	B = 1


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


class Sub(Base):
	class_base_n: ClassVar['int'] = 0
	base_n: int

	def __init__(self, n: int) -> None:
		self.base_n = n

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
		self.inst_var0 = None
		self.inst_var1: Sub
		self.inst_arr = []
		self.inst_map = {}
		self.inst_tsiis = []
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

	def hex(self, n: int, p: CP[str]) -> None:
		p.hex()
		CP(n).hex()


class FuncOps:
	def kw_params(self, **kwargs: int) -> str:
		a = self.kw_params(a=1, b=2)
		return ''


class AccessOps(Sub):
	sub_s: str

	def __init__(self) -> None:
		super().__init__(0)
		self.sub_s = ''

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
		print(Values.A)
		d: dict[Values, str] = {
			Values.A: 'A',
			Values.B: 'B',
		}

	def indexer(self, arr_p: CP[list[int]], arr_sp: CSP[list[int]], arr_ar: CRef[list[int]]) -> None:
		print(arr_p.raw[0])
		print(arr_sp.raw[0])
		print(arr_ar.raw[0])


@Embed.alias('Alias2')
class Alias:
	inner: 'Alias.Inner'

	def __init__(self) -> None:
		self.inner = Alias.Inner()

	class Values(Enum):
		A = 1
		B = 2

	@Embed.alias('Inner2')
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


class GenericOps(Generic[T]):
	def __init__(self) -> None: ...

	def temporal(self, value: T) -> None:
		a = value

	def new(self) -> None:
		a = GenericOps[int]()


@Embed.struct
@Embed.meta('class', 'meta')
class Struct:
	a: Annotated[int, '@var int']
	b: Annotated[str, '@var str']

	def __init__(self, a: int, b: str) -> None:
		self.a = a
		self.b = b


class ForCompound:
	class Proto(Protocol): ...

	class DeclPropsBase:
		anno_n: int
		move_s: str

		def __init__(self) -> None:
			self.anno_n: int = 0
			self.move_s = ''

	class DeclProps(DeclPropsBase):
		cls_b: ClassVar[bool] = True
		move_dsn: dict[str, int]

		def __init__(self, n: int, s: str) -> None:
			super().__init__()
			self.anno_n = int(s)
			self.move_s = str(n)
			self.move_dsn = {s: n}

	class ClassMethod:
		@classmethod
		def make(cls: type[Self]) -> Self:
			inst = cls()
			return inst

		@classmethod
		def immutable_returns(cls) -> Annotated[str, Embed.immutable]:
			...

	class Method:
		def immutable_returns(self) -> Annotated[CP[str], Embed.immutable]:
			...

	class DeclEnum:
		class ES(Enum):
			AS = 'a'
			BS = 'b'

		class EN(Enum):
			AN = 0
			BN = 1

		def literalize(self) -> None:
			print(ForCompound.DeclEnum.ES.AS.name)
			print(ForCompound.DeclEnum.ES.BS.name)
			print(ForCompound.DeclEnum.ES.AS.value)
			print(ForCompound.DeclEnum.ES.BS.value)
			print(ForCompound.DeclEnum.EN.AN.name)
			print(ForCompound.DeclEnum.EN.BN.name)

	class Operators:
		# comparison
		def __eq__(self, other: Annotated['ForCompound.Operators', Embed.immutable]) -> bool: ...
		def __ne__(self, other: Annotated['ForCompound.Operators', Embed.immutable]) -> bool: ...
		def __lt__(self, other: Annotated['ForCompound.Operators', Embed.immutable]) -> bool: ...
		def __gt__(self, other: Annotated['ForCompound.Operators', Embed.immutable]) -> bool: ...
		def __le__(self, other: Annotated['ForCompound.Operators', Embed.immutable]) -> bool: ...
		def __ge__(self, other: Annotated['ForCompound.Operators', Embed.immutable]) -> bool: ...
		# arithmetic
		def __add__(self, value: Annotated[int, Embed.immutable]) -> int: ...
		def __sub__(self, value: Annotated[int, Embed.immutable]) -> int: ...
		def __mul__(self, value: Annotated[int, Embed.immutable]) -> int: ...
		def __mod__(self, value: Annotated[int, Embed.immutable]) -> int: ...
		def __truediv__(self, value: Annotated[int, Embed.immutable]) -> int: ...
		# bitwise
		def __and__(self, value: Annotated[int, Embed.immutable]) -> int: ...
		def __or__(self, value: Annotated[int, Embed.immutable]) -> int: ...
		# indexer
		def __getitem__(self, key: str) -> CRef[Sub]: ...
		# XXX C++では不要なため、出力対象から除外する
		@Embed.python
		def __setitem__(self, key: str, value: CRef[Sub]) -> None: ...
		def usage(self, other: 'ForCompound.Operators', sub: Sub) -> None:
			if self is other and self is not other: ...
			if self < other and self > other and self <= other and self >= other: ...
			print(self + 1, self - 1, self * 1, self % 1, self / 1)
			print(self & 1, self | 1)
			if self['a'].raw is not sub:
				self['a'] = CRef(sub)

	class Modifier:
		@Embed.public
		def _to_public(self) -> None: ...
		@Embed.protected
		def to_protected(self) -> None: ...
		@Embed.private
		def to_private(self) -> None: ...
		@Embed.pure
		def pure(self) -> None: ...
		def mod_mutable(self, s_m: Annotated[str, Embed.mutable], s_i: str, ns_i: list[int], dsn_i: dict[str, int], func_i: Callable[[], None]) -> None: ...

	def closure(self) -> None:
		def bind_ref() -> None: ...
		@Embed.closure_bind(self)
		def bind_copy() -> None: ...


class ForClassExpose:
	@Embed.python
	class Class: ...
	@Embed.python
	class Enums(Enum): ...
	@Embed.python
	def class_method(self) -> None: ...
	@Embed.python
	def method(self) -> None: ...
	@Embed.alias('method')
	def method_cpp(self) -> None: ...


@Embed.python
def func_expose() -> None: ...


class ForTemplate:
	class TClass(Generic[T]):
		def __init__(self, v: T) -> None: ...
		@classmethod
		def class_method_t(cls, v2: T2) -> T2: ...
		@classmethod
		def class_method_t_and_class_t(cls, v: T, v2: T2) -> T2: ...
		def method_t(self, v2: T2) -> T2: ...
		def method_t_and_class_t(self, v: T, v2: T2) -> T2: ...

	class T2Class(Generic[T2]): ...

	def unpack(self, p: T | None) -> T: ...
	def unpack_call(self) -> None:
		a = self.unpack(ForTemplate())


def template_unpack(v: T | None) -> T: ...
def template_unpack_call() -> None:
	a = template_unpack(ForTemplate())


def template_func(v: T) -> T: ...


class ForFlows:
	def if_elif_else(self) -> None:
		if 1: ...
		elif 2: ...
		else: ...

	def while_only(self) -> None:
		while True: ...

	def for_range(self, strs: list[str]) -> None:
		for i in range(2): ...
		for i in range(len(strs)): ...

	def for_enumerate(self, strs: list[str]) -> None:
		for index, value in enumerate([1]): ...
		for index, value in enumerate(strs): ...

	def for_dict(self, dsn: DSI, psn: CP[dict[str, int]], dpp: dict[CP[int], CP[int]]) -> None:
		for key in {'a': 1}.keys(): ...
		for value in {'a': 1}.values(): ...
		for key, value in {'a': 1}.items(): ...

		for key in dsn.keys(): ...
		for value in dsn.values(): ...
		for key, value in dsn.items(): ...

		for key in psn.on.keys(): ...
		for value in psn.on.values(): ...
		for key, value in psn.on.items(): ...

		for kp in dpp.keys(): ...
		for vp in dpp.values(): ...
		for kp, vp in dpp.items(): ...

	def for_each(self, strs: list[str], ts: list[tuple[int, int, int]], cps: list[CPConst[int]]) -> None:
		for n in [1]: ...
		for s in strs: ...
		for e1, e2, e3 in ts: ...
		for cp in cps: ...

	def try_catch_throw(self) -> None:
		try: ...
		except RuntimeError as e:
			raise Exception() from e
		except Exception as e:
			raise e


class ForAssign:
	def anno(self) -> None:
		n: int = 1
		ns: list[int] = []
		dsn: dict[str, int] = {}
		ts: tuple[bool, int, str] = (True, 1, 'a')
		static_dsn: Annotated[dict[str, int], Embed.static] = {'a': 1}

	def move(self) -> None:
		s = 'a'
		ss = ['a']
		dsns = {'a': [1]}
		ts = True, 1, 'b'

	def aug(self, n: int, s: str) -> None:
		n += 1
		s += str(n)

	def move_unpack(self, bnf: tuple[bool, int, float], tsiis: list[TSII]) -> None:
		tb, tn, tf = bnf
		ts0, ti1, ti2 = tsiis[0]
		s0 = tsiis[0][0]
		i1 = tsiis[0][1]
		i2 = tsiis[0][2]

	def for_enum(self) -> None:
		ea = Values.A
		es = [Values.A]
		des = {
			Values.A: 'A',
			Values.B: 'B',
		}
		e = es[0]
		s = des[Values.A]


class ForSimple:
	def delete_list_dict(self, ns: list[int], dsn: dict[str, int]) -> None:
		del ns[0]
		del ns[1], ns[2]
		del dsn['a']
		del dsn['b'], dsn['c']

	def return_none(self) -> None:
		return

	def return_value(self) -> int:
		return 0

	def asserts(self) -> None:
		assert True
		assert 1 == 0, Exception

	def pass_only(self) -> None:
		pass

	def break_continue(self) -> None:
		for i in range(1):
			if i == 0: continue
			if i != 0: break

		while True:
			if 1 == 0: continue
			if 1 != 0: break

	def comment(self) -> None:
		# abc
		...


class ForIndexer:
	def list_slice(self, ns: list[int]) -> None:
		ns[1:]
		ns[:5]
		ns[3:9:2]

	def string_slice(self, s: str) -> None:
		s[1:]
		s[:5]


class ForFuncCall:
	class CallableType:
		func: Callable[[int, str], bool]

		def __init__(self, func: Callable[[int, str], bool]) -> None:
			self.func = func

	def move_assign(self, caller: CallableType) -> None:
		func = caller.func
		b0 = caller.func(0, '')
		b1 = func(0, '')

	class Func:
		def print(self) -> None:
			print('message. %d, %f, %s', 1, 1.0, 'abc')

		def func_self(self, s: str) -> int: ...
		@classmethod
		def func_cls(cls, n: int) -> str: ...

		def c_func(self) -> None:
			ds = Embed.static({'f': c_func_ref(ForFuncCall.Func.func_self)})
			n: int = c_func_invoke(self, ds['f'], 'a')

			dc = Embed.static({'f': c_func_ref(ForFuncCall.Func.func_cls)})
			s: str = dc['f'](1)

	@Embed.alias('Class2')
	class Class:
		def literalize(self, t: type[Alias]) -> None:
			print(self.__class__.__name__)
			print(self.__module__)
			print(Alias.__module__)
			print(Alias.Inner.__name__)
			print(Alias.in_local.__name__)
			print(Alias.in_local.__qualname__)
			print(Alias.Inner.func.__qualname__)
			print(t.__name__)
			print(Values.A.name)

	class Cast:
		def cast_binary(self) -> None:
			f_to_n = int(1.0)
			n_to_f = float(1)
			n_to_b = bool(1)
			e_to_n = int(Values.A)

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

		def cast_enum(self) -> None:
			e = Values(0)
			n = int(Values.A)

	class Copy:
		def __py_copy__(self, origin: 'CRef[ForFuncCall.Copy]') -> None:
			...

		def move_obj(self, via: 'CRef[ForFuncCall.Copy]', to: 'CRef[ForFuncCall.Copy]') -> None:
			to.copy(via)

		def move_scalar(self, output: 'CRef[int]') -> None:
			output.copy(CRef(1))

	class List:
		def pop(self, ns: list[int]) -> None:
			ns.pop(1)
			ns.pop()

		def insert(self, ns: list[int], n: int) -> None:
			ns.insert(1, n)

		def extend(self, ns0: list[int], ns1: list[int]) -> None:
			ns0.extend(ns1)

		def clear(self, ns: list[int]) -> None:
			ns.clear()

		def contains(self, ns: list[int]) -> None:
			b_in = 1 in ns
			b_not_in = 1 not in ns

		def fill(self, n: int) -> None:
			n_x3 = [n] * 3

		def len(self, ns: list[int]) -> None:
			len(ns)

	class Dict:
		def pop(self, dsn: dict[str, int]) -> None:
			dsn.pop('a')
			dsn.pop('b')

		def keys(self, dsn: dict[str, int]) -> None:
			list(dsn.keys())

		def values(self, dsn: dict[str, int]) -> None:
			list(dsn.values())

		def get(self, dsn: dict[str, int]) -> None:
			n = dsn.get('a', 1)

		def clear(self, dsn: dict[str, int]) -> None:
			dsn.clear()

		def contains(self, dsn: dict[str, int]) -> None:
			b_in = 'a' in dsn
			b_not_in = 'a' not in dsn

		def len(self, dsn: dict[str, int]) -> None:
			len(dsn)

	class String:
		def mod_methods(self, s: str) -> None:
			str('').split(',')
			str('').join(['a'])
			str('').replace('from', 'to')
			str('').lstrip(' ')
			str('').rstrip(' ')
			str('').strip(' ')
			s.split(',')
			s.join(['a'])
			s.replace('from', 'to')
			s.lstrip(' ')
			s.rstrip(' ')
			s.strip(' ')

		def find_methods(self, s: str) -> None:
			str('').find('a')
			str('').rfind('a')
			str('').count('.')
			str('').startswith('')
			str('').endswith('')
			s.find('a')
			s.rfind('a')
			s.count('.')
			s.startswith('')
			s.endswith('')

		def format(self, s: str) -> None:
			'{n}, {f}, {b}, {s}, {sp}, {p}'.format(n=1, f=2.0, b=True, s='3', sp=s, p=CP(self))
			s.format(1, 2, 3)

		def encode(self, s: str, b: bytes) -> None:
			s.encode()
			''.encode()

		def decode(self, b: bytes) -> None:
			b.decode()

		def len(self, s: str) -> None:
			len(s)


class ForBinaryOperator:
	def char_op_by_str(self, string: str) -> None:
		a = string[0] >= char('A')
		b = string[0] <= char('Z')
		c = char(string[0])

	def decimal_mod(self) -> None:
		print((1.0 % 1) % (1 % 1.0))

	def comparison(self, v1: int, v2: str, c1: Base, c2: Sub, t1: type[int], t2: type[str]) -> None:
		v_eq = (v1 is v2) and (v1 is not v2) and not v1
		c_eq = (c1 is c2) and (c1 is not c2) and not c1
		t_eq = (t1 is t2) and (t1 is not t2) and not t1


T_Args = TypeVarTuple('T_Args')
T_Base = TypeVar('T_Base', bound=Base)


class ForTemplateClass:
	class Delegate(Generic[*T_Args]):
		def bind(self, obj: CP[T], method: Annotated[Callable[[T, *T_Args], None], Embed.immutable]) -> None: ...
		def invoke(self, *args: *T_Args) -> None: ...

	class A:
		def func(self, b: bool, c: int) -> None: ...

	def bind_call(self, a: CP[A]) -> None:
		d = ForTemplateClass.Delegate[bool, int]()
		d.bind(a, c_func_ref(ForTemplateClass.A.func))
		d.invoke(True, 1)

	def boundary_call(self, t: type[T_Base]) -> T_Base:
		return t()


class ForComp:
	def list_comp_from_list(self, ns: list[int], cps: list[CPConst[int]], ts: list[tuple[int, int, int]]) -> None:
		[l[0] for l in [[1]]]
		[n for n in ns]
		[cp for cp in cps]
		[e0 + e1 + e2 for e0, e1, e2 in ts]
		[i for i in range(len(ns))]
		[(i, n) for i, n in enumerate(ns)]

	def list_comp_from_dict(self, dsn: DSI, psn: CP[dict[str, int]], dpp: dict[CP[int], CP[int]]) -> None:
		[s for s in {'a': 1}.keys()]
		[n for n in {'a': 1}.values()]
		[(s, n) for s, n in {'a': 1}.items()]

		[s for s in dsn.keys()]
		[n for n in dsn.values()]
		[(s, n) for s, n in dsn.items()]

		[s for s in psn.on.keys()]
		[n for n in psn.on.values()]
		[(s, n) for s, n in psn.on.items()]

		[kp for kp in dpp.keys()]
		[vp for vp in dpp.values()]
		[(kp, vp) for kp, vp in dpp.items()]

	def dict_comp_from_list(self, ns: list[int], cps: list[CPConst[int]], ts: list[tuple[int, int, int]]) -> None:
		{l[0]: l for l in [[1]]}
		{n: n for n in ns}
		{cp: cp for cp in cps}
		{e0: (e1, e2) for e0, e1, e2 in ts}

	def dict_comp_from_dict(self, dsn: DSI, psn: CP[dict[str, int]], dpp: dict[CP[int], CP[int]]) -> None:
		{s: s for s in {'a': 1}.keys()}
		{n: n for n in {'a': 1}.values()}
		{s: n for s, n in {'a': 1}.items()}

		{s: s for s in dsn.keys()}
		{n: n for n in dsn.values()}
		{s: n for s, n in dsn.items()}

		{s: s for s in psn.on.keys()}
		{n: n for n in psn.on.values()}
		{s: n for s, n in psn.on.items()}

		{kp: kp for kp in dpp.keys()}
		{vp: vp for vp in dpp.values()}
		{kp: vp for kp, vp in dpp.items()}


class ForLambda:
	def expression(self) -> None:
		f = lambda: 1
		n = f()
		s = (lambda: 'a')()
		if (lambda: True)(): ...
