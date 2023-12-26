from py2cpp.ast.path import EntryPath
from py2cpp.errors import LogicError
import py2cpp.node.definition as defs
from py2cpp.node.node import Node
from py2cpp.node.symboldb import SymbolDB


class Classify:
	def __init__(self, db: SymbolDB) -> None:
		self.__db = db

	def type_of(self, node: defs.Symbol | defs.GenericType | defs.Null) -> defs.Types:
		return self.__type_of(node, self.__resolve_symbol(node))
	
	def __resolve_symbol(self, node: defs.Symbol | defs.GenericType | defs.Null) -> str:
		if node.is_a(defs.This):
			return node.namespace
		elif node.is_a(defs.ThisVar):
			return EntryPath.join(node.namespace, EntryPath(node.to_string()).last()[0]).origin
		elif node.is_a(defs.Symbol):
			return node.to_string()
		elif node.is_a(defs.GenericType):
			return node.as_a(defs.GenericType).symbol.to_string()
		else:
			return node.to_string()

	def __type_of(self, node: defs.Symbol | defs.GenericType | defs.Null | defs.Literal | defs.Types, symbol: str) -> defs.Types:
		symbols = EntryPath(symbol)
		first, _ = symbols.first()[0]
		remain = symbols.shift(1)
		candidates = [
			EntryPath.join(node.scope, first),
			EntryPath.join(node.module.path, first),
		]
		for candidate in candidates:
			if candidate.origin in self.__db:
				continue

			row = self.__db[candidate.origin]
			if not remain.valid:
				return row.types

			founded = self.__type_of(row.types, remain.origin)
			if founded:
				return founded

		raise LogicError(f'Symbol not defined. node: {node}, symbol: {symbol}')

	def literal_of(self, node: defs.Literal) -> defs.Types:
		return self.__type_of(node, node.alias_name)

	def result_of(self, expression: Node) -> defs.Types:
		handler = Handler(self)
		for node in expression.calculated():
			handler.on_action(node)

		return handler.result()


class Handler:
	def __init__(self, classify: Classify) -> None:
		self.__classify = classify
		self.__stack: list[defs.Types] = []

	def result(self) -> defs.Types:
		return self.__stack.pop()

	def on_action(self, node: Node) -> None:
		self.__stack.append(self.invoke(node))

	def invoke(self, node: Node) -> defs.Types:
		handler_name = f'on_{node.identifer}'
		handler = getattr(self, handler_name)
		keys = reversed([key for key, _ in handler.__annotations__.items() if key != 'return'])
		annotations = {key: handler.__annotations__[key] for key in keys}
		args = {node: node, **{key: self.__stack.pop() for key in annotations.keys()}}
		valids = [True for key, arg in args.items() if isinstance(arg, annotations[key])]
		if len(valids) != len(args):
			raise LogicError(f'Invalid arguments. node: {node}, actual {len(valids)} to expected {len(args)}')

		return handler(node, **args)

	# Primary

	def on_symbol(self, node: defs.Symbol) -> defs.Types:
		return self.__classify.type_of(node)

	def on_this(self, node: defs.This) -> defs.Types:
		return self.__classify.type_of(node)

	def on_indexer(self, node: defs.Indexer) -> defs.Types:
		return self.__classify.type_of(node.symbol)

	def on_list_type(self, node: defs.ListType) -> defs.Types:
		return self.on_generic_type(node)

	def on_dict_type(self, node: defs.DictType) -> defs.Types:
		return self.on_generic_type(node)

	def on_union_type(self, node: defs.UnionType) -> defs.Types:
		raise LogicError(f'Operation not supoorted. {node}')

	def on_generic_type(self, node: defs.GenericType) -> defs.Types:
		return self.__classify.type_of(node.symbol)

	def on_func_call(self, node: defs.FuncCall, calls: defs.Function) -> defs.Types:
		return self.__classify.type_of(calls.return_type)

	# Common

	def on_argument(self, node: defs.Argument, value: defs.Types) -> defs.Types:
		return value

	# Operator

	def on_sum(self, node: defs.Sum, left: defs.Class, right: defs.Class) -> defs.Types:
		return self.on_binary_operator(node, left, right, '__add__')

	def on_binary_operator(self, node: defs.Sum, left: defs.Class, right: defs.Class, operator: str) -> defs.Types:
		methods = [method for method in left.as_a(defs.Class).methods if method.symbol.to_string () == operator]
		if len(methods) == 0:
			raise LogicError(f'Operation not allowed. {node}, {left}, {right}, {operator}')

		other = methods[0].parameters.pop()
		var_types = [other.var_type] if not other.var_type.is_a(defs.UnionType) else other.var_type.as_a(defs.UnionType).types
		for var_type in var_types:
			if self.__classify.type_of(var_type.one_of(defs.Symbol | defs.GenericType)) == right:
				return right

		raise LogicError(f'Operation not allowed. {node}, {left}, {right}, {operator}')

	# Literal

	def on_integer(self, node: defs.Integer) -> defs.Types:
		return self.__classify.literal_of(node)

	def on_float(self, node: defs.Float) -> defs.Types:
		return self.__classify.literal_of(node)

	def on_string(self, node: defs.String) -> defs.Types:
		return self.__classify.literal_of(node)

	def on_truthy(self, node: defs.Truthy) -> defs.Types:
		return self.__classify.literal_of(node)

	def on_falsy(self, node: defs.Falsy) -> defs.Types:
		return self.__classify.literal_of(node)

	def on_list(self, node: defs.List) -> defs.Types:
		return self.__classify.literal_of(node)

	def on_dict(self, node: defs.Dict) -> defs.Types:
		return self.__classify.literal_of(node)
