from typing import Callable, TypeAlias, TypeVar, cast

from py2cpp.analyze.symbol import SymbolRaw
from py2cpp.ast.dsn import DSN
from py2cpp.errors import LogicError
from py2cpp.lang.implementation import override
import py2cpp.lang.sequence as seqs
import py2cpp.node.definition as defs

T_Ref = TypeVar('T_Ref', bound='Reflection')


class Reflection:
	def __init__(self, via: SymbolRaw, inject_schema: dict[str, SymbolRaw | list[SymbolRaw]]) -> None:
		self._via = via
		self._inject_schema = inject_schema

	def _schema(self, key: str) -> SymbolRaw:
		if key in self._inject_schema and type(self._inject_schema[key]) is SymbolRaw:
			return cast(SymbolRaw, self._inject_schema[key])

		raise LogicError()

	def _schemata(self, key: str) -> list[SymbolRaw]:
		if key in self._inject_schema and type(self._inject_schema[key]) is list:
			return cast(list[SymbolRaw], self._inject_schema[key])

		raise LogicError()

	@property
	def types(self) -> defs.ClassDef:
		return self._via.types

	@property
	def shorthand(self) -> str:
		return str(self._via)

	def is_a(self, ctor: type['Reflection']) -> bool:
		return isinstance(self, ctor)


class Object(Reflection): ...


class Instance(Object):
	@property
	def klass(self) -> SymbolRaw:
		...

	@property
	def props(self) -> dict[str, SymbolRaw]:
		...

	@property
	def methods(self) -> dict[str, SymbolRaw]:
		...


class Function(Object):
	@property
	def parameters(self) -> dict[str, SymbolRaw]:
		return {parameter.decl.symbol.tokens: parameter for parameter in self._schemata('parameters')}

	@property
	def returns(self) -> SymbolRaw:
		return self._schema('returns')

	def invoke(self, *arguments: SymbolRaw) -> SymbolRaw:
		map_props = TemplateManipulator.unpack_symbols(parameters=list(arguments))
		t_map_props = TemplateManipulator.unpack_templates(parameters=list(self.parameters.values()), returns=self.returns)
		t_map_returns = TemplateManipulator.unpack_templates(returns=self.returns)
		updates = TemplateManipulator.make_updates(t_map_returns, t_map_props)
		return TemplateManipulator.actualize(self.returns, map_props, updates)


class Closure(Function): ...


class Method(Function):
	@property
	def klass(self) -> SymbolRaw:
		return self._schema('klass')

	@override
	def invoke(self, *arguments: SymbolRaw) -> SymbolRaw:
		map_props = TemplateManipulator.unpack_symbols(klass=list(arguments)[0], parameters=list(arguments)[1:])
		t_map_props = TemplateManipulator.unpack_templates(klass=self.klass, parameters=list(self.parameters.values()))
		t_map_returns = TemplateManipulator.unpack_templates(returns=self.returns)
		updates = TemplateManipulator.make_updates(t_map_returns, t_map_props)
		return TemplateManipulator.actualize(self.returns, map_props, updates)


class ClassMethod(Method): ...
class Constructor(Method): ...


TemplateMap: TypeAlias = dict[str, defs.TemplateClass]
SymbolMap: TypeAlias = dict[str, SymbolRaw]
UpdateMap: TypeAlias = dict[str, str]


class TemplateManipulator:
	@classmethod
	def unpack_templates(cls, **attrs: SymbolRaw | list[SymbolRaw]) -> TemplateMap:
		expand_attrs = seqs.expand(attrs, iter_key='attrs')
		return {path: attr.types for path, attr in expand_attrs.items() if isinstance(attr.types, defs.TemplateClass)}

	@classmethod
	def unpack_symbols(cls, **attrs: SymbolRaw | list[SymbolRaw]) -> SymbolMap:
		return seqs.expand(attrs, iter_key='attrs')

	@classmethod
	def make_updates(cls, t_map_primary: TemplateMap, t_map_props: TemplateMap) -> UpdateMap:
		updates: UpdateMap = {}
		for primary_path, t_primary in t_map_primary.items():
			founds = [prop_path for prop_path, t_prop in t_map_props.items() if t_prop == t_primary]
			if founds:
				updates[primary_path] = founds[0]

		return updates

	@classmethod
	def actualize(cls, primary: SymbolRaw, actual_props: SymbolMap, updates: UpdateMap) -> SymbolRaw:
		primary_bodies = [prop_path for primary_path, prop_path in updates.items() if DSN.elem_counts(primary_path) == 1]
		if primary_bodies:
			return actual_props[primary_bodies[0]]

		for primary_path, prop_path in updates.items():
			seqs.update(primary.attrs, primary_path, actual_props[prop_path], iter_key='attrs')

		return primary


class Builder:
	def __init__(self, via: SymbolRaw) -> None:
		self.__via = via
		self.__schemata: dict[str, SymbolRaw | list[SymbolRaw]] = {}

	def schema(self, **schema: SymbolRaw | list[SymbolRaw]) -> 'Builder':
		self.__schemata = {**self.__schemata, **schema}
		return self

	def build(self, target: type[T_Ref]) -> T_Ref:
		ctors: dict[type[defs.ClassDef], type[Reflection]] = {
			defs.Function: Function,
			defs.ClassMethod: ClassMethod,
			defs.Method: Method,
			defs.Constructor: Constructor,
		}
		ctor = ctors[self.__via.types.__class__]
		if not issubclass(ctor, target):
			raise LogicError()

		return ctor(self.__via, self.__schemata)
