from enum import Enum, EnumType
from types import NoneType
from typing import Any, Callable, cast
from unittest import TestCase

from rogw.tranp.lang.annotation import override
from rogw.tranp.lang.inspection import Typehint, Inspector, ClassTypehint, FunctionTypehint, ScalarTypehint
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
		self.assertEqual(expected['raw'], hint.raw)
		self.assertEqual(expected['origin'], hint.origin)

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
		self.assertEqual(expected['null'], hint.is_null)
		self.assertEqual(expected['generic'], hint.is_generic)
		self.assertEqual(expected['list'], hint.is_list)
		self.assertEqual(expected['union'], hint.is_union)
		self.assertEqual(expected['nullable'], hint.is_nullable)
		self.assertEqual(expected['enum'], hint.is_enum)

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
		self.assertEqual(expected, [cast(ScalarTypehint, hint).origin for hint in ScalarTypehint(origin).sub_types])

	@data_provider([
		(Values, [Values.A]),
	])
	def test_enum_members(self, origin: EnumType, expected: list[Enum]) -> None:
		self.assertEqual(expected, ScalarTypehint(origin).enum_members)


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
		(Sub.__init__, 'function'),  # XXX タイプから取得するとFunctionTypeになり、メソッドであるか否かを判別できない ※Pythonの仕様
		(Sub.cls_func, 'classmethod'),
		(Sub.self_func, 'function'),  # XXX タイプから取得するとFunctionTypeになり、メソッドであるか否かを判別できない ※Pythonの仕様
		(Sub.prop, 'method'),
		(Sub().cls_func, 'classmethod'),
		(Sub().self_func, 'method'),
		(func, 'function'),
	])
	def test_func_type(self, origin: Callable, expected: str) -> None:
		hint = FunctionTypehint(origin)
		self.assertEqual(expected, hint.func_type)

	@data_provider([
		(Sub.__init__, {'args': {}, 'returns': None}),
		(Sub.cls_func, {'args': {'n': int}, 'returns': str}),
		(Sub.self_func, {'args': {'l': list, 'd': dict}, 'returns': tuple}),
		# (Sub.prop, {'args': {}, 'returns': int}),
		(Sub().cls_func, {'args': {'n': int}, 'returns': str}),
		(Sub().self_func, {'args': {'l': list, 'd': dict}, 'returns': tuple}),
		(func, {'args': {'n': int}, 'returns': str}),
	])
	def test_signature(self, origin: Callable, expected: dict[str, Any]) -> None:
		hint = FunctionTypehint(origin)
		self.assertEqual(expected['args'], {key: arg.origin for key, arg in hint.args.items()})
		self.assertEqual(expected['returns'], hint.returns.origin)


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

	@data_provider([
		(Sub, Sub.__init__),
	])
	def test_constructor(self, origin: type, expected: Callable) -> None:
		hint = ClassTypehint(origin)
		self.assertEqual(expected, hint.constructor.raw)

	@data_provider([
		(Sub, {'class_vars': {'n': int, 'l': list}, 'self_vars': {'d': dict, 't': tuple}, 'methods': ['__init__', '__self_attributes__', 'cls_method', 'self_method']}),
	])
	def test_schema(self, origin: type, expected: dict[str, Any]) -> None:
		hint = ClassTypehint(origin)
		self.assertEqual(expected['class_vars'], {key: var.origin for key, var in hint.class_vars.items()})
		self.assertEqual(expected['self_vars'], {key: var.origin for key, var in hint.self_vars.items()})
		self.assertEqual(expected['methods'], [key for key in hint.methods.keys()])


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
		self.assertEqual(expected, type(Inspector.resolve(origin)))
