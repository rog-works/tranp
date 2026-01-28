from collections.abc import Callable
from enum import Enum, EnumType
from types import FunctionType, MethodType, NoneType, UnionType
from typing import Annotated, Any, ClassVar, Generic, TypeVar, cast
from unittest import TestCase

from rogw.tranp.lang.typehint import ClassTypehint, FuncClasses, FunctionTypehint, ScalarTypehint, Typehints
from rogw.tranp.test.helper import data_provider
from rogw.tranp.test.validation import validation


class Values(Enum):
	A = 1


T = TypeVar('T')
class Gen(Generic[T]): ...


class Base:
	cn: ClassVar[int] = 0
	an: Annotated[int, 'meta']
	d: dict[str, int]
	__private: int

	def __init__(self) -> None:
		self.n = 0
		self.d = {}
		self.__private = 0

	@classmethod
	def cls_method(cls, n: int) -> str: ...


class Sub(Base):
	cl: ClassVar['list[int]'] = []
	t: tuple[str, int, bool]
	obj: Base
	p: 'Gen[Base] | None'

	def __init__(self) -> None:
		super().__init__()
		self.t = '', 0, False
		self.obj = Base()
		self.p = None

	def self_method(self, l: list[int], d: 'dict[str, int]') -> 'tuple[str, int, bool]': ...

	@property
	def prop(self) -> int: ...


class Annos:
	cls_self: ClassVar[Annotated['Annos | None', 'meta']] = None
	a_imported: Annotated['ScalarTypehint', 'meta']
	an: Annotated['int', 'meta']
	ad: Annotated['dict[str, int]', 'meta']


def func(n: int, fn: 'int', an: Annotated[int, 'meta'], afn: Annotated['int', 'meta']) -> str: ...


class TestScalarTypehint(TestCase):
	@data_provider([
		(int, {'raw': int, 'origin': int}),
		(list, {'raw': list, 'origin': list}),
		(list[int], {'raw': list[int], 'origin': list}),
		(dict, {'raw': dict, 'origin': dict}),
		(dict[str, int], {'raw': dict[str, int], 'origin': dict}),
		(tuple, {'raw': tuple, 'origin': tuple}),
		(tuple[str, int, bool], {'raw': tuple[str, int, bool], 'origin': tuple}),
		(type, {'raw': type, 'origin': type}),
		(type[str], {'raw': type[str], 'origin': type}),
		(int | str, {'raw': int | str, 'origin': UnionType}),
		(int | None, {'raw': int | None, 'origin': UnionType}),
		(Base | None, {'raw': Base | None, 'origin': UnionType}),
		(Gen[Base] | None, {'raw': Gen[Base] | None, 'origin': UnionType}),
		(None, {'raw': None, 'origin': None}),
		(Values, {'raw': Values, 'origin': Values}),
	])
	def test_origins(self, origin: type, expected: dict[str, type]) -> None:
		hint = ScalarTypehint(origin)
		self.assertEqual(hint.raw, expected['raw'])
		self.assertEqual(hint.origin, expected['origin'])

	@data_provider([
		(int, {'null': False, 'generic': False, 'union': False, 'nullable': False, 'enum': False}),
		(list, {'null': False, 'generic': True, 'union': False, 'nullable': False, 'enum': False}),
		(list[int], {'null': False, 'generic': True, 'union': False, 'nullable': False, 'enum': False}),
		(dict, {'null': False, 'generic': True, 'union': False, 'nullable': False, 'enum': False}),
		(dict[str, int], {'null': False, 'generic': True, 'union': False, 'nullable': False, 'enum': False}),
		(tuple, {'null': False, 'generic': True, 'union': False, 'nullable': False, 'enum': False}),
		(tuple[str, int, bool], {'null': False, 'generic': True, 'union': False, 'nullable': False, 'enum': False}),
		(type, {'null': False, 'generic': True, 'union': False, 'nullable': False, 'enum': False}),
		(type[str], {'null': False, 'generic': True, 'union': False, 'nullable': False, 'enum': False}),
		(int | str, {'null': False, 'generic': False, 'union': True, 'nullable': False, 'enum': False}),
		(int | None, {'null': False, 'generic': False, 'union': True, 'nullable': True, 'enum': False}),
		(Base | None, {'null': False, 'generic': False, 'union': True, 'nullable': True, 'enum': False}),
		(Gen[Base] | None, {'null': False, 'generic': False, 'union': True, 'nullable': True, 'enum': False}),
		(None, {'null': True, 'generic': False, 'union': False, 'nullable': False, 'enum': False}),
		(Values, {'null': False, 'generic': False, 'union': False, 'nullable': False, 'enum': True}),
	])
	def test_states(self, origin: type, expected: dict[str, bool]) -> None:
		hint = ScalarTypehint(origin)
		self.assertEqual(hint.is_null, expected['null'])
		self.assertEqual(hint.is_generic, expected['generic'])
		self.assertEqual(hint.is_union, expected['union'])
		self.assertEqual(hint.is_nullable, expected['nullable'])
		self.assertEqual(hint.is_enum, expected['enum'])

	@data_provider([
		(int, []),
		(list, []),
		(list[int], [int]),
		(dict, []),
		(dict[str, int], [str, int]),
		(tuple, []),
		(tuple[str, int, bool], [str, int, bool]),
		(type, []),
		(type[str], [str]),
		(int | str, [int, str]),
		(int | None, [int, NoneType]),
		(Base | None, [Base, NoneType]),
		(Gen[Base] | None, [Gen, NoneType]),
		(Values, []),
	])
	def test_sub_types(self, origin: type, expected: list[type]) -> None:
		self.assertEqual([cast(ScalarTypehint, hint).origin for hint in ScalarTypehint(origin).sub_types], expected)

	@data_provider([
		(Values, [Values.A]),
	])
	def test_enum_members(self, origin: EnumType, expected: list[Enum]) -> None:
		self.assertEqual(ScalarTypehint(origin).enum_members, expected)


class TestFunctionTypehint(TestCase):
	_sub: ClassVar[Sub] = Sub()

	@data_provider([
		(Sub.__init__, {'origin': FunctionType, 'raw': Sub.__init__}),
		(Sub.cls_method, {'origin': MethodType, 'raw': Sub.cls_method}),
		(Sub.self_method, {'origin': FunctionType, 'raw': Sub.self_method}),
		(Sub.prop, {'origin': property, 'raw': Sub.prop}),
		(_sub.cls_method, {'origin': MethodType, 'raw': _sub.cls_method}),
		(_sub.self_method, {'origin': MethodType, 'raw': _sub.self_method}),
		(func, {'origin': FunctionType, 'raw': func}),
	])
	def test_origins(self, origin: Callable, expected: dict[str, Any]) -> None:
		hint = FunctionTypehint(origin)
		self.assertEqual(hint.origin, expected['origin'])
		self.assertEqual(hint.raw, expected['raw'])

	@data_provider([
		(Sub.__init__, FuncClasses.Function),  # XXX タイプから取得した場合、メソッドであるか否かを判別できない ※Pythonの仕様
		(Sub.cls_method, FuncClasses.ClassMethod),
		(Sub.self_method, FuncClasses.Function),  # XXX タイプから取得した場合、メソッドであるか否かを判別できない ※Pythonの仕様
		(Sub.prop, FuncClasses.Method),
		(_sub.cls_method, FuncClasses.ClassMethod),
		(_sub.self_method, FuncClasses.Method),
		(func, FuncClasses.Function),
	])
	def test_func_type(self, origin: Callable, expected: FuncClasses) -> None:
		hint = FunctionTypehint(origin)
		self.assertEqual(hint.func_class, expected)

	@data_provider([
		(Sub.__init__, {'args': {}, 'returns': None}),
		(Sub.cls_method, {'args': {'n': int}, 'returns': str}),
		(Sub.self_method, {'args': {'l': list, 'd': dict}, 'returns': tuple}),
		(Sub.prop, {'args': {}, 'returns': int}),
		(_sub.cls_method, {'args': {'n': int}, 'returns': str}),
		(_sub.self_method, {'args': {'l': list, 'd': dict}, 'returns': tuple}),
		(func, {'args': {'n': int, 'fn': int, 'an': int, 'afn': int}, 'returns': str}),
	])
	def test_signature(self, origin: Callable, expected: dict[str, Any]) -> None:
		hint = FunctionTypehint(origin)
		self.assertEqual({key: arg.origin for key, arg in hint.args.items()}, expected['args'])
		self.assertEqual(hint.returns.origin, expected['returns'])


class TestClassTypehint(TestCase):
	@data_provider([
		(Sub, Sub.__init__),
		(Gen[str], Gen[str].__init__),
	])
	def test_constructor(self, origin: type, expected: Callable) -> None:
		hint = ClassTypehint(origin)
		self.assertEqual(hint.constructor.raw, expected)

	@data_provider([
		(Sub, {'origin': Sub, 'raw': Sub}),
		(Gen[str], {'origin': Gen, 'raw': Gen[str]}),
	])
	def test_origins(self, origin: type, expected: dict[str, Any]) -> None:
		hint = ClassTypehint(origin)
		self.assertEqual(hint.origin, expected['origin'])
		self.assertEqual(hint.raw, expected['raw'])

	@data_provider([
		(Sub, {'is_generic': False, 'sub_types': []}),
		(Gen[str], {'is_generic': True, 'sub_types': [str]}),
	])
	def test_generics(self, origin: type, expected: dict[str, Any]) -> None:
		hint = ClassTypehint(origin)
		self.assertEqual(hint.is_generic, expected['is_generic'])
		self.assertEqual([sub_type.origin for sub_type in hint.sub_types], expected['sub_types'])

	@data_provider([
		(Sub, {
			'class_vars': {'cn': (int, None), 'cl': (list, None)},
			'self_vars': {'an': (int, 'meta'), 'd': (dict, None), 't': (tuple, None), 'obj': (Base, None), 'p': (UnionType, None)},
			'methods': [Sub.__init__.__name__, Sub.cls_method.__name__, Sub.self_method.__name__, 'prop'],
		}),
		(Gen[str], {
			'class_vars': {},
			'self_vars': {},
			'methods': [],
		}),
		(Annos, {
			'class_vars': {'cls_self': (UnionType, 'meta')},
			'self_vars': {'a_imported': (ScalarTypehint, 'meta'), 'an': (int, 'meta'), 'ad': (dict, 'meta')},
			'methods': [],
		}),
	])
	def test_schema(self, origin: type, expected: dict[str, Any]) -> None:
		hint = ClassTypehint(origin)
		self.assertEqual({key: (var.origin, var.meta(str)) for key, var in hint.class_vars().items()}, expected['class_vars'])
		self.assertEqual({key: (var.origin, var.meta(str)) for key, var in hint.self_vars(lookup_private=False).items()}, expected['self_vars'])
		self.assertEqual([key for key in hint.methods.keys()], expected['methods'])


class TestTypehints(TestCase):
	@data_provider([
		(int, {'type': ScalarTypehint, 'meta': None}),
		(str, {'type': ScalarTypehint, 'meta': None}),
		(float, {'type': ScalarTypehint, 'meta': None}),
		(bool, {'type': ScalarTypehint, 'meta': None}),
		(list, {'type': ScalarTypehint, 'meta': None}),
		(list[int], {'type': ScalarTypehint, 'meta': None}),
		(dict, {'type': ScalarTypehint, 'meta': None}),
		(dict[str, int], {'type': ScalarTypehint, 'meta': None}),
		(tuple[str, int, bool], {'type': ScalarTypehint, 'meta': None}),
		(int | str, {'type': ScalarTypehint, 'meta': None}),
		(type, {'type': ScalarTypehint, 'meta': None}),
		(type[str], {'type': ScalarTypehint, 'meta': None}),
		(None, {'type': ScalarTypehint, 'meta': None}),
		(type(None), {'type': ScalarTypehint, 'meta': None}),
		(Base | None, {'type': ScalarTypehint, 'meta': None}),
		(Gen[Base] | None, {'type': ScalarTypehint, 'meta': None}),
		(Annotated[int, 'metadata'], {'type': ScalarTypehint, 'meta': 'metadata'}),
		(func, {'type': FunctionTypehint, 'meta': None}),
		(Typehints.resolve, {'type': FunctionTypehint, 'meta': None}),
		(Typehints, {'type': ClassTypehint, 'meta': None}),
	])
	def test_resolve(self, origin: type, expected: dict[str, Any]) -> None:
		hint = Typehints.resolve(origin)
		self.assertEqual(type(hint), expected['type'])
		self.assertEqual(hint.meta(str), expected['meta'])

	@data_provider([
		(Sub, {
			'type': {'class_vars': {'cn': ScalarTypehint, 'cl': ScalarTypehint}, 'self_vars': {'an': ScalarTypehint, 'd': ScalarTypehint, 't': ScalarTypehint, 'obj': ClassTypehint, 'p': ScalarTypehint}},
			'meta': {'class_vars': {'cn': None, 'cl': None}, 'self_vars': {'an': 'meta', 'd': None, 't': None, 'obj': None, 'p': None}},
		}),
		(func, {
			'type': {'args': {'n': ScalarTypehint, 'fn': ScalarTypehint, 'an': ScalarTypehint, 'afn': ScalarTypehint}, 'returns': ScalarTypehint},
			'meta': {'args': {'n': None, 'fn': None, 'an': 'meta', 'afn': 'meta'}, 'returns': None},
		}),
	])
	def test_resolve_internal(self, origin: type, expected: dict[str, Any]) -> None:
		hint = Typehints.resolve(origin)
		if isinstance(hint, FunctionTypehint):
			self.assertEqual({key: type(arg) for key, arg in hint.args.items()}, expected['type']['args'])
			self.assertEqual({key: arg.meta(str) for key, arg in hint.args.items()}, expected['meta']['args'])
			self.assertEqual(type(hint.returns), expected['type']['returns'])
			self.assertEqual(hint.returns.meta(str), expected['meta']['returns'])
		elif isinstance(hint, ClassTypehint):
			self.assertEqual({key: type(class_var) for key, class_var in hint.class_vars().items()}, expected['type']['class_vars'])
			self.assertEqual({key: class_var.meta(str) for key, class_var in hint.class_vars().items()}, expected['meta']['class_vars'])
			self.assertEqual({key: type(self_var) for key, self_var in hint.self_vars(lookup_private=False).items()}, expected['type']['self_vars'])
			self.assertEqual({key: self_var.meta(str) for key, self_var in hint.self_vars(lookup_private=False).items()}, expected['meta']['self_vars'])
		else:
			self.fail()

	def test_validation(self) -> None:
		self.assertTrue(validation(Sub, lookup_private=False))
