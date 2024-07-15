from enum import Enum, EnumType
from types import NoneType
from typing import Any, Callable, cast
from unittest import TestCase

from rogw.tranp.lang.annotation import override
from rogw.tranp.lang.inspection import Annotation, AnnotationResolver, ClassAnnotation, FunctionAnnotation, ScalarAnnotation
from rogw.tranp.test.helper import data_provider


class TestScalarAnnotation(TestCase):
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
		anno = ScalarAnnotation(origin)
		self.assertEqual(expected['raw'], anno.raw)
		self.assertEqual(expected['origin'], anno.origin)

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
		anno = ScalarAnnotation(origin)
		self.assertEqual(expected['null'], anno.is_null)
		self.assertEqual(expected['generic'], anno.is_generic)
		self.assertEqual(expected['list'], anno.is_list)
		self.assertEqual(expected['union'], anno.is_union)
		self.assertEqual(expected['nullable'], anno.is_nullable)
		self.assertEqual(expected['enum'], anno.is_enum)

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
		self.assertEqual(expected, [cast(ScalarAnnotation, anno).origin for anno in ScalarAnnotation(origin).sub_types])

	@data_provider([
		(Values, [Values.A]),
	])
	def test_enum_members(self, origin: EnumType, expected: list[Enum]) -> None:
		self.assertEqual(expected, ScalarAnnotation(origin).enum_members)


def func(n: int) -> str: ...


class TestFunctionAnnotation(TestCase):
	class Base:
		def __init__(self) -> None: ...
		@classmethod
		def cls_func(cls, n: int) -> str: ...
		def self_func(self, l: list[int], d: dict[str, int]) -> tuple[int, str, bool]: ...
		@property
		def prop(self) -> int: ...

	class Sub(Base): ...

	@data_provider([
		(Sub.__init__, {'static': False, 'method': False, 'function': True}),  # FIXME 静的に取得するとFunctionTypeになり、メソッドであるか否かを判別できない
		(Sub.cls_func, {'static': True, 'method': True, 'function': False}),
		(Sub.self_func, {'static': False, 'method': False, 'function': True}),  # FIXME 静的に取得するとFunctionTypeになり、メソッドであるか否かを判別できない
		# FIXME (Sub.prop, {'static': False, 'method': False, 'function': False}),  # FIXME Functionですらない
		(Sub().cls_func, {'static': True, 'method': True, 'function': False}),
		(Sub().self_func, {'static': False, 'method': True, 'function': False}),
		(func, {'static': False, 'method': False, 'function': True}),
	])
	def test_states(self, origin: Callable, expected: dict[str, bool]) -> None:
		anno = FunctionAnnotation(origin)
		self.assertEqual(expected['static'], anno.is_static)
		self.assertEqual(expected['method'], anno.is_method)
		self.assertEqual(expected['function'], anno.is_function)

	@data_provider([
		(Sub.cls_func, Sub),
		(Sub().cls_func, Sub),
		(Sub().self_func, Sub),
	])
	def test_receiver(self, origin: Callable, expected: type) -> None:
		anno = FunctionAnnotation(origin)
		self.assertEqual(expected, anno.receiver if anno.is_static else anno.receiver.__class__)

	@data_provider([
		(Sub.__init__,),  # FIXME 静的に取得するとreceiverを取得できない
		(Sub.self_func,),  # FIXME 静的に取得するとreceiverを取得できない
		(func,),
	])
	def test_receiver_error(self, origin: Callable) -> None:
		with self.assertRaises(AttributeError):
			FunctionAnnotation(origin).receiver

	@data_provider([
		(Sub.__init__, {'args': {}, 'returns': None}),
		(Sub.cls_func, {'args': {'n': int}, 'returns': str}),
		(Sub.self_func, {'args': {'l': list, 'd': dict}, 'returns': tuple}),
		# FIXME (Sub.prop, {'args': {}, 'returns': int}),
		(Sub().cls_func, {'args': {'n': int}, 'returns': str}),
		(Sub().self_func, {'args': {'l': list, 'd': dict}, 'returns': tuple}),
		(func, {'args': {'n': int}, 'returns': str}),
	])
	def test_signature(self, origin: Callable, expected: dict[str, Any]) -> None:
		anno = FunctionAnnotation(origin)
		self.assertEqual(expected['args'], {key: arg.origin for key, arg in anno.args.items()})
		self.assertEqual(expected['returns'], anno.returns.origin)


class TestClassAnnotation(TestCase):
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
		anno = ClassAnnotation(origin)
		self.assertEqual(expected, anno.constructor.raw)

	@data_provider([
		(Sub, {'class_vars': {'n': int, 'l': list}, 'self_vars': {'d': dict, 't': tuple}, 'methods': ['__init__', '__self_attributes__', 'cls_method', 'self_method']}),
	])
	def test_schema(self, origin: type, expected: dict[str, Any]) -> None:
		anno = ClassAnnotation(origin)
		self.assertEqual(expected['class_vars'], {key: var.origin for key, var in anno.class_vars.items()})
		self.assertEqual(expected['self_vars'], {key: var.origin for key, var in anno.self_vars.items()})
		self.assertEqual(expected['methods'], [key for key in anno.methods.keys()])


class TestAnnotationResolver(TestCase):
	@data_provider([
		(int, ScalarAnnotation),
		(str, ScalarAnnotation),
		(float, ScalarAnnotation),
		(bool, ScalarAnnotation),
		(list, ScalarAnnotation),
		(list[int], ScalarAnnotation),
		(dict, ScalarAnnotation),
		(dict[str, int], ScalarAnnotation),
		(tuple[str, int, bool], ScalarAnnotation),
		(int | str, ScalarAnnotation),
		(type, ScalarAnnotation),
		(type[str], ScalarAnnotation),
		(None, ScalarAnnotation),
		(type(None), ScalarAnnotation),
		(func, FunctionAnnotation),
		(AnnotationResolver.resolve, FunctionAnnotation),
		(AnnotationResolver, ClassAnnotation),
	])
	def test_resolve(self, origin: type, expected: Annotation) -> None:
		self.assertEqual(expected, type(AnnotationResolver.resolve(origin)))
