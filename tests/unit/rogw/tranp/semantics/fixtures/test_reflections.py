from collections.abc import Callable, Iterator
from enum import Enum
from os import path as os_path
from typing import Annotated, Any, ClassVar, Generic, Self, TypeAlias, TypeVar, TypeVarTuple, cast
from yaml import safe_load as yaml_safe_load

from tests.unit.rogw.tranp.semantics.reflection.fixtures.test_db_combine import S, C, A

DSI: TypeAlias = dict[str, int]
DSI2: TypeAlias = dict[str, DSI]
C2: TypeAlias = C


value: int = 0


class Base(C):
	base_str: str

	def __init__(self) -> None:
		self.base_str = S
		# comment

	@classmethod
	def return_cls(cls: type[Self]) -> type[Self]:
		base = cls.return_cls()
		inst = cls()
		return cls

	@classmethod
	def make_base(cls) -> 'Base':
		inst = cls()
		return inst

	def return_self(self: Self) -> Self:
		base = self.return_self()
		return self


class Sub(Base):
	numbers: 'list[int]'
	# C: C XXX Pythonの構文的に前方宣言はNG

	def __init__(self) -> None:
		super().__init__()
		self.numbers = []

	class Inner:
		value: ClassVar[str] = ''

		@classmethod
		def class_func(cls) -> dict[str, int]:
			return {cls.value: value}

	@property
	def C(self) -> C:
		...

	@property
	def first_number(self) -> int:
		return self.numbers[0]

	def local_ref(self) -> None:
		value = False
		print(value)

	def member_ref(self: Self) -> None:
		a = self.numbers
		b = self.first_number
		c = self.C
		sub = self.return_self()
		sub_cls = Sub.return_cls()

	def member_write(self) -> None:
		A.nx = 2
		Sub.Inner.value = 'update'

	def param_ref(self, param: int) -> None:
		print(param)

	def list_ref(self, subs: 'list[Sub]') -> None:
		print(self.numbers[0])
		print(subs[0].numbers)

	def base_ref(self) -> None:
		print(self.base_str)

	def returns(self) -> str:
		return self.base_str

	def yields(self) -> Iterator[str]:
		yield self.base_str

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

	def kw_params(self, **kwargs: int) -> str:
		a = self.kw_params(a=1, b=2)
		return ''

	def indexer_access(self, ns: list[int], ss: list[str], s: str) -> None:
		ns0 = ns[0]
		ss0 = ss[0]
		s0 = s[0]
		ns_slice0 = ns[0:]
		ns_slice1 = ns[:1]
		ns_slice2 = ns[0:1]
		ss_slice = ss[0:5:2]
		s_slice = s[0:]
		dsn = cast(dict[str, int], {})

	def type_props(self) -> None:
		a = self.__class__.__name__
		b = self.__class__
		c = self.__module__

	def list_expand(self) -> None:
		a = [1, *[]]
		b = [*[], [2]]
		c = [*(1,), *[2]]

	def dict_expand(self) -> None:
		a = {'a': 1, **{}}
		b = {**{}, 'a': {'b': 1}}

	def tuple_arg(self) -> None:
		a = isinstance(1, (int, float))
		b = issubclass(int, (int, float))

	def decl_tuple(self, p: tuple[int, int, int]) -> tuple[str, str, str]:
		a = (1, 'a', False)
		b = p
		c = self.decl_tuple(p)
		return ('', '', '')

	def imported_inner_type_ref(self, b: 'C.AA') -> None:
		a = C.AA()


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


class AliasOps:
	def func(self, z2: C2) -> None:
		d: DSI = {'s': value}
		d_in_v = d['s']

		d2: DSI2 = {'s2': d}
		d2_in_dsi = d2['s']
		d2_in_dsi_in_v = d2['s2']['s']

		z2_in_x = z2.x
		new_z2_in_x = C2().x


class TupleOps:
	def unpack(self) -> None:
		for key0, value0 in {'a': 1}.items(): ...
		for value1 in {'a': 1}.values(): ...
		for key1 in {'a': 1}.keys(): ...
		for key2 in {'a': 1}: ...

		d: DSI2 = {'a': {'b': 2}}
		for key10, value10 in d.items(): ...
		for value11 in d.values(): ...
		for key11 in d.keys(): ...
		for key12 in d: ...

	def assign(self, index: int) -> None:
		t = (1, 'a')
		t0 = t[0]
		t1 = t[1]
		tu = t[index]
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
	class Values(Enum):
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

	def comparison(self) -> None:
		a = EnumOps.Values.A == EnumOps.Values.B
		b = EnumOps.Values.A != EnumOps.Values.B
		c = EnumOps.Values.A is EnumOps.Values.B
		d = EnumOps.Values.A is not EnumOps.Values.B


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


T = TypeVar('T')


class GenericOps(Generic[T]):
	def __init__(self) -> None: ...

	def temporal(self, value: T) -> None:
		a = value

	def new(self) -> None:
		a = GenericOps[int]()

	def cast(self, sub: 'GenericOps[Sub]') -> None:
		b = cast(GenericOps[Base], sub)


class WithOps:
	def file_load(self) -> None:
		dir = os_path.dirname(__file__)
		with open(os_path.join(dir, 'hoge.yml'), encoding='utf-8') as f:
			content = cast(dict[str, Any], yaml_safe_load(f))


class ForFuncCall:
	@classmethod
	def cls_call(cls) -> str:
		return cls.cls_call()

	def self_call(self) -> int:
		return self.self_call()

	def func_call(self) -> None:
		def func() -> bool: ...
		func()

	def relay_call(self) -> 'ForFuncCall':
		self.relay_call().relay_call()
		return self

	def call_to_call(self) -> None:
		ForFuncCall().self_call()

	def indexer_call(self, arr: 'list[ForFuncCall]') -> None:
		arr[0].self_call()

	def callable_call(self, func: Callable[[int, str], T]) -> T:
		return func(1, 'a')


class ForFunction:
	def anno_param(self, an: Annotated[int, 'meta'], ab: Annotated['bool', 'meta']) -> None:
		...


class ForClass:
	class DeclThisVar:
		cls_n: ClassVar[int] = 0
		anno_dsn: dict[str, int]
		n: int
		sp: str | None
		ab: Annotated[bool, 'meta']
		ac: Annotated['ForClass.DeclThisVar | None', 'meta']

		def __init__(self, n: int = cls_n) -> None:
			self.anno_dsn: dict[str, int] = {'a': ForClass.DeclThisVar.cls_n}
			self.n = n
			self.sp = None
			self.ab = False
			self.ac = None
			self.n = int(cast(str, self.sp))


class ForEnum:
	class ES(Enum):
		A = 'a'
		B = 'b'

	class EN(Enum):
		A = 0
		B = 1

	def ref_props(self) -> None:
		es_a_name = ForEnum.ES.A.name
		es_a_value = ForEnum.ES.A.value
		en_b_name = ForEnum.EN.B.name
		en_b_value = ForEnum.EN.B.value


T_Args = TypeVarTuple('T_Args')
T_Base = TypeVar('T_Base', bound=Base)


class ForTemplateClass:
	class G1(Generic[T]):
		v: T

		def __init__(self, v: T) -> None:
			self.v = v

	class G2(Generic[T]):
		v: 'ForTemplateClass.G1[T]'

		def __init__(self, v: 'ForTemplateClass.G1[T]') -> None:
			self.v = v

	class G3(G1[int]):
		def v_ref(self) -> None:
			g1 = ForTemplateClass.G1(0)
			g1_v = g1.v
			g2 = ForTemplateClass.G2(g1)
			g2_v = g2.v
			g3_v = self.v

	class Delegate(Generic[*T_Args]):
		def bind(self, obj: T, method: Callable[[T, *T_Args], None]) -> None: ...
		def invoke(self, *args: *T_Args) -> None: ...

	class A:
		def func(self, b: bool, c: int) -> None: ...

	def bind_call(self) -> None:
		a = ForTemplateClass.A()
		d = ForTemplateClass.Delegate[bool, int]()
		d.bind(a, ForTemplateClass.A.func)
		d.invoke(True, 1)

	def boundary_call(self, t: type[T_Base]) -> T_Base:
		return t()


class ForLambda:
	def expression(self) -> None:
		lambda: 'a'
		f = lambda: False
		b = f()
		ns = (lambda: [1])()
