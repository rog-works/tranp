from enum import Enum, EnumType
from types import FunctionType, MethodType, NoneType, UnionType
from typing import Any, Callable, ClassVar, Generic, TypeVar, cast
from unittest import TestCase

from rogw.tranp.lang.inspection import FuncClasses, Typehint, Inspector, ClassTypehint, FunctionTypehint, ScalarTypehint
from rogw.tranp.test.helper import data_provider


class Values(Enum):
	A = 1


T = TypeVar('T')
class Gen(Generic[T]): ...


class Base:
	n: ClassVar[int] = 0
	d: dict[str, int]

	def __init__(self) -> None:
		self.d: dict[str, int] = {}

	@classmethod
	def cls_method(cls, n: int) -> str: ...


class Sub(Base):
	l: ClassVar[list[int]] = []
	t: tuple[str, int, bool]
	obj: Base | None
	p: 'Gen[Base] | None'

	def __init__(self) -> None:
		super().__init__()
		self.t: tuple[str, int, bool] = '', 0, False
		self.obj: Base | None = None
		self.p: Gen[Base] | None = None

	def self_method(self, l: list[int], d: 'dict[str, int]') -> 'tuple[str, int, bool]': ...

	@property
	def prop(self) -> int: ...


def func(n: int) -> str: ...


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
		(func, {'args': {'n': int}, 'returns': str}),
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
			'class_vars': {'n': int, 'l': list},
			'self_vars': {'d': dict, 't': tuple, 'obj': UnionType, 'p': UnionType},
			'methods': ['__init__', 'cls_method', 'self_method', 'prop'],
		}),
		(Gen[str], {
			'class_vars': {},
			'self_vars': {},
			'methods': [],
		}),
	])
	def test_schema(self, origin: type, expected: dict[str, Any]) -> None:
		hint = ClassTypehint(origin)
		self.assertEqual({key: var.origin for key, var in hint.class_vars.items()}, expected['class_vars'])
		self.assertEqual({key: var.origin for key, var in hint.self_vars.items()}, expected['self_vars'])
		self.assertEqual([key for key in hint.methods.keys()], expected['methods'])


class TestInspector(TestCase):
	@data_provider([
		(int, ScalarTypehint),
		(str, ScalarTypehint),
		(float, ScalarTypehint),
		(bool, ScalarTypehint),
		(list, ScalarTypehint),
		(list[int], ScalarTypehint),
		(dict, ScalarTypehint),
		(dict[str, int], ScalarTypehint),
		(tuple[str, int, bool], ScalarTypehint),
		(int | str, ScalarTypehint),
		(type, ScalarTypehint),
		(type[str], ScalarTypehint),
		(None, ScalarTypehint),
		(type(None), ScalarTypehint),
		(Base | None, ScalarTypehint),
		(Gen[Base] | None, ScalarTypehint),
		(func, FunctionTypehint),
		(Inspector.resolve, FunctionTypehint),
		(Inspector, ClassTypehint),
	])
	def test_resolve(self, origin: type, expected: Typehint) -> None:
		self.assertEqual(type(Inspector.resolve(origin)), expected)

	def test_validation(self) -> None:
		self.assertTrue(Inspector.validation(Sub))
