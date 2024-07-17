from enum import Enum, EnumType
from types import NoneType
from typing import Any, Callable, Generic, TypeVar, cast
from unittest import TestCase

from rogw.tranp.lang.annotation import override
from rogw.tranp.lang.inspection import FuncClasses, SelfAttributes, Typehint, Inspector, ClassTypehint, FunctionTypehint, ScalarTypehint
from rogw.tranp.test.helper import data_provider


class TestScalarTypehint(TestCase):
	class Values(Enum):
		A = 1

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
		(int | str, {'raw': int | str, 'origin': int | str}),  # XXX origin=UnionTypeの方が良い？
		(int | None, {'raw': int | None, 'origin': int | None}),  # XXX origin=UnionTypeの方が良い？
		(None, {'raw': None, 'origin': None}),
		(Values, {'raw': Values, 'origin': Values}),
	])
	def test_origins(self, origin: type, expected: dict[str, type]) -> None:
		hint = ScalarTypehint(origin)
		self.assertEqual(hint.raw, expected['raw'])
		self.assertEqual(hint.origin, expected['origin'])

	@data_provider([
		(int, {'null': False, 'generic': False, 'list': False, 'union': False, 'nullable': False, 'enum': False}),
		(list, {'null': False, 'generic': True, 'list': True, 'union': False, 'nullable': False, 'enum': False}),
		(list[int], {'null': False, 'generic': True, 'list': True, 'union': False, 'nullable': False, 'enum': False}),
		(dict, {'null': False, 'generic': True, 'list': False, 'union': False, 'nullable': False, 'enum': False}),
		(dict[str, int], {'null': False, 'generic': True, 'list': False, 'union': False, 'nullable': False, 'enum': False}),
		(tuple, {'null': False, 'generic': True, 'list': False, 'union': False, 'nullable': False, 'enum': False}),
		(tuple[str, int, bool], {'null': False, 'generic': True, 'list': False, 'union': False, 'nullable': False, 'enum': False}),
		(type, {'null': False, 'generic': True, 'list': False, 'union': False, 'nullable': False, 'enum': False}),
		(type[str], {'null': False, 'generic': True, 'list': False, 'union': False, 'nullable': False, 'enum': False}),
		(int | str, {'null': False, 'generic': False, 'list': False, 'union': True, 'nullable': False, 'enum': False}),
		(int | None, {'null': False, 'generic': False, 'list': False, 'union': True, 'nullable': True, 'enum': False}),
		(None, {'null': True, 'generic': False, 'list': False, 'union': False, 'nullable': False, 'enum': False}),
		(Values, {'null': False, 'generic': False, 'list': False, 'union': False, 'nullable': False, 'enum': True}),
	])
	def test_states(self, origin: type, expected: dict[str, bool]) -> None:
		hint = ScalarTypehint(origin)
		self.assertEqual(hint.is_null, expected['null'])
		self.assertEqual(hint.is_generic, expected['generic'])
		self.assertEqual(hint.is_list, expected['list'])
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
		(Values, []),
	])
	def test_sub_types(self, origin: type, expected: list[type]) -> None:
		self.assertEqual([cast(ScalarTypehint, hint).origin for hint in ScalarTypehint(origin).sub_types], expected)

	@data_provider([
		(Values, [Values.A]),
	])
	def test_enum_members(self, origin: EnumType, expected: list[Enum]) -> None:
		self.assertEqual(ScalarTypehint(origin).enum_members, expected)


def func(n: int) -> str: ...


class TestFunctionTypehint(TestCase):
	class Base:
		def __init__(self) -> None: ...
		@classmethod
		def cls_func(cls, n: int) -> str: ...
		def self_func(self, l: list[int], d: dict[str, int]) -> tuple[int, str, bool]: ...
		@property
		def prop(self) -> int: ...

	class Sub(Base): ...

	@data_provider([
		(Sub.__init__, FuncClasses.Function),  # XXX タイプから取得した場合、メソッドであるか否かを判別できない ※Pythonの仕様
		(Sub.cls_func, FuncClasses.ClassMethod),
		(Sub.self_func, FuncClasses.Function),  # XXX タイプから取得した場合、メソッドであるか否かを判別できない ※Pythonの仕様
		(Sub.prop, FuncClasses.Method),
		(Sub().cls_func, FuncClasses.ClassMethod),
		(Sub().self_func, FuncClasses.Method),
		(func, FuncClasses.Function),
	])
	def test_func_type(self, origin: Callable, expected: FuncClasses) -> None:
		hint = FunctionTypehint(origin)
		self.assertEqual(hint.func_class, expected)

	@data_provider([
		(Sub.__init__, {'args': {}, 'returns': None}),
		(Sub.cls_func, {'args': {'n': int}, 'returns': str}),
		(Sub.self_func, {'args': {'l': list, 'd': dict}, 'returns': tuple}),
		(Sub.prop, {'args': {}, 'returns': int}),
		(Sub().cls_func, {'args': {'n': int}, 'returns': str}),
		(Sub().self_func, {'args': {'l': list, 'd': dict}, 'returns': tuple}),
		(func, {'args': {'n': int}, 'returns': str}),
	])
	def test_signature(self, origin: Callable, expected: dict[str, Any]) -> None:
		hint = FunctionTypehint(origin)
		self.assertEqual({key: arg.origin for key, arg in hint.args.items()}, expected['args'])
		self.assertEqual(hint.returns.origin, expected['returns'])


class TestClassTypehint(TestCase):
	class Base:
		n: int = 0

		def __init__(self) -> None:
			self.d: dict[str, int] = {}

		@classmethod
		def __self_attributes__(cls) -> dict[str, type]:
			return {'d': dict[str, int]}

		@classmethod
		def cls_method(cls) -> None: ...

	class Sub(Base):
		l: list[int] = []

		def __init__(self) -> None:
			super().__init__()
			self.t: tuple[str, int, bool] = '', 0, False

		@classmethod
		@override
		def __self_attributes__(cls) -> dict[str, type]:
			attrs = super().__self_attributes__()
			return {**attrs, 't': tuple[str, int, bool]}

		def self_method(self) -> None: ...

		@property
		def prop(self) -> None: ...

	T = TypeVar('T')
	class Gen(Generic[T]): ...

	@data_provider([
		(Sub, Sub.__init__),
		(Gen[str], Gen[str].__init__),
	])
	def test_constructor(self, origin: type, expected: Callable) -> None:
		hint = ClassTypehint(origin)
		self.assertEqual(hint.constructor.raw, expected)

	@data_provider([
		(Sub, {
			'origin': Sub,
			'raw': Sub,
			'sub_types': [],
			'class_vars': {'n': int, 'l': list},
			'self_vars': {'d': dict, 't': tuple},
			'methods': ['__init__', '__self_attributes__', 'cls_method', 'self_method', 'prop'],
		}),
		(Gen[str], {
			'origin': Gen,
			'raw': Gen[str],
			'sub_types': [str],
			'class_vars': {},
			'self_vars': {},
			'methods': [],
		}),
	])
	def test_schema(self, origin: type, expected: dict[str, Any]) -> None:
		hint = ClassTypehint(origin)
		self.assertEqual(hint.origin, expected['origin'])
		self.assertEqual(hint.raw, expected['raw'])
		self.assertEqual([sub_type.origin for sub_type in hint.sub_types], expected['sub_types'])
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
		(func, FunctionTypehint),
		(Inspector.resolve, FunctionTypehint),
		(Inspector, ClassTypehint),
	])
	def test_resolve(self, origin: type, expected: Typehint) -> None:
		self.assertEqual(type(Inspector.resolve(origin)), expected)

	def test_validation(self) -> None:
		self.assertTrue(Inspector.validation(TestClassTypehint.Sub))
