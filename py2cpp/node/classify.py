from py2cpp.ast.dns import domainize
from py2cpp.ast.path import EntryPath
from py2cpp.errors import LogicError
import py2cpp.node.definition as defs
from py2cpp.node.node import Node
from py2cpp.node.symboldb import SymbolDB, SymbolRow


class Classify:
	def __init__(self, db: SymbolDB) -> None:
		self.__db = db

	def type_of(self, node: defs.Symbol | defs.GenericType | defs.Literal | defs.Types) -> defs.Types:
		founded = self.__type_of(node, node.module.path, node.scope, self.__resolve_symbol(node))
		if founded is not None:
			return founded

		raise LogicError(f'Symbol not defined. node: {node}')
	
	def __resolve_symbol(self, node: defs.Symbol | defs.GenericType | defs.Literal | defs.Types) -> str:
		if node.is_a(defs.This, defs.ThisVar):
			return node.tokens
		elif node.is_a(defs.GenericType):
			return node.as_a(defs.GenericType).symbol.tokens
		elif node.is_a(defs.Literal):
			return node.as_a(defs.Literal).class_symbol_alias
		elif node.is_a(defs.Types):
			return node.as_a(defs.Types).symbol.tokens
		else:
			# その他のSymbol
			return node.tokens

	def __type_of(self, node: Node, module_path: str, scope: str, symbol: str) -> defs.Types | None:
		symbols = EntryPath(symbol)
		symbol_types = None
		symbol_counts = len(symbols.elements)
		remain_counts = symbol_counts
		while remain_counts > 0:
			candidate = EntryPath.join(*symbols.elements[0:(symbol_counts - (remain_counts - 1))]).origin
			found_row = self.__fetch_symbol_row(module_path, scope, candidate)
			if found_row is None:
				break

			symbol_types = found_row.types
			remain_counts -= 1

		if symbol_types and remain_counts == 0:
			return symbol_types

		remain_symbol = symbols.shift(symbol_counts - remain_counts).origin
		if symbol_types and symbol_types.is_a(defs.Class):
			return self.__type_of(symbol_types, symbol_types.module.path, symbol_types.block.scope, remain_symbol)
		elif node.is_a(defs.Class):
			return self.__type_of_from_class_chain(node.as_a(defs.Class), remain_symbol)

		return None

	def __fetch_symbol_row(self, module_path: str, scope: str, symbol: str) -> SymbolRow | None:
		domain_id = domainize(scope, symbol)
		domain_name = domainize(module_path, symbol)
		if domain_id in self.__db:
			return self.__db[domain_id]
		elif domain_name in self.__db:
			return self.__db[domain_name]

		return None

	def __type_of_from_class_chain(self, class_types: defs.Class, symbol: str) -> defs.Types | None:
		for symbol_node in class_types.parents:
			parent_types = self.__type_of(symbol_node, symbol_node.module.path, symbol_node.scope, symbol_node.tokens)
			if parent_types is None:
				break

			founded = self.__type_of(parent_types, parent_types.module.path, parent_types.block.scope, symbol)
			if founded:
				return founded

		return None

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
		handler_name = f'on_{node.classification}'
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

	def on_var(self, node: defs.Var) -> defs.Types:
		return self.__classify.type_of(node)

	def on_this(self, node: defs.This) -> defs.Types:
		return self.__classify.type_of(node)

	def on_this_var(self, node: defs.ThisVar) -> defs.Types:
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

	def on_func_call(self, node: defs.FuncCall, calls: defs.Function, arguments: list[defs.Argument]) -> defs.Types:
		if calls.is_a(defs.Constructor):
			return self.__classify.type_of(calls.as_a(defs.Constructor).class_symbol)
		else:
			return self.__classify.type_of(calls.return_type.var_type)

	def on_super(self, node: defs.Super, calls: defs.Function, arguments: list[defs.Argument]) -> defs.Types:
		return self.__classify.type_of(node.class_symbol)

	# Common

	def on_argument(self, node: defs.Argument, value: defs.Types) -> defs.Types:
		return value

	# Operator

	def on_sum(self, node: defs.Sum, left: defs.Class, right: defs.Class) -> defs.Types:
		return self.on_binary_operator(node, left, right, '__add__')

	def on_binary_operator(self, node: defs.Sum, left: defs.Class, right: defs.Class, operator: str) -> defs.Types:
		methods = [method for method in left.as_a(defs.Class).methods if method.symbol.tokens == operator]
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
		return self.__classify.type_of(node)

	def on_float(self, node: defs.Float) -> defs.Types:
		return self.__classify.type_of(node)

	def on_string(self, node: defs.String) -> defs.Types:
		return self.__classify.type_of(node)

	def on_truthy(self, node: defs.Truthy) -> defs.Types:
		return self.__classify.type_of(node)

	def on_falsy(self, node: defs.Falsy) -> defs.Types:
		return self.__classify.type_of(node)

	def on_list(self, node: defs.List) -> defs.Types:
		return self.__classify.type_of(node)

	def on_dict(self, node: defs.Dict) -> defs.Types:
		return self.__classify.type_of(node)
