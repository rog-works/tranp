from typing import TypeAlias

from py2cpp.ast.travarsal import EntryPath
from py2cpp.errors import LogicError
from py2cpp.module.module import Module
from py2cpp.module.modules import Modules
import py2cpp.node.definition as defs
from py2cpp.node.node import Node

SymbolDB: TypeAlias = dict[str, defs.Types]


class Classify:
	def __init__(self, db: SymbolDB) -> None:
		self.__db = db

	def type_of(self, node: defs.Symbol | defs.GenericType | defs.Null) -> defs.Types:
		return self.__type_of(node.scope, node.to_string() if node.is_a(defs.Symbol) else node.as_a(defs.GenericType).symbol.to_string())

	def __type_of(self, scope: str, symbol: str) -> defs.Types:
		symbols = EntryPath(symbol)
		first, _ = symbols.first()[0]
		remain = symbols.shift(1)
		candidates = [
			EntryPath.join(scope, first),
			EntryPath.join(first),
		]
		for candidate in candidates:
			if candidate.origin in self.__db:
				continue

			ctor = self.__db[candidate.origin]
			if not remain.valid:
				return ctor

			founded = self.__type_of(ctor.block.scope, remain.origin)
			if founded:
				return founded

		raise LogicError(f'Symbol not defined. scope: {scope}, symbol: {symbol}')

	def literal_of(self, node: defs.Literal) -> defs.Types:
		return self.__type_of(node.scope, node.classification)

	def result_of(self, expression: Node) -> defs.Types:
		handler = Classify.Handler(self)
		for node in expression.calculated():
			handler.on_action(node)

		return handler.result()

	class Handler:
		def __init__(self, classify: 'Classify') -> None:
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


class SymbolDBFactory:
	def create(self, modules: Modules) -> SymbolDB:
		main = modules.main
		db, decl_vars, import_nodes = self.__pluck_main(main)

		for import_node in import_nodes:
			module = modules.load(import_node.module_path.to_string())
			db = {**db, **self.__pluck_imported(main, module)}

		for module in modules.core_libralies:
			db = {**db, **self.__pluck_imported(main, module)}

		for var in decl_vars:
			path = EntryPath.join(var.scope, var.symbol.to_string())
			db[path.origin] = self.__resolve_symbol(var, db)

		return db

	def __pluck_main(self, module: Module) -> tuple[SymbolDB, list[defs.AnnoAssign | defs.MoveAssign], list[defs.Import]]:
		db: SymbolDB = {}
		decl_vars: list[defs.AnnoAssign | defs.MoveAssign] = []
		import_nodes: list[defs.Import] = []
		for node in module.entrypoint(Node).calculated():
			if isinstance(node, (defs.Function, defs.Class, defs.Enum)):
				path = EntryPath.join(node.scope, node.symbol.to_string())
				db[path.origin] = node

			if type(node) is defs.Import:
				import_nodes.append(node)

			if type(node) is defs.Entrypoint:
				decl_vars.extend(node.decl_vars)
			elif type(node) is defs.Function:
				decl_vars.extend(node.block.decl_vars)
			elif type(node) is defs.ClassMethod:
				decl_vars.extend(node.block.decl_vars)
			elif type(node) is defs.Method:
				decl_vars.extend(node.block.decl_vars)
			elif type(node) is defs.Class:
				decl_vars.extend(node.vars)
			elif type(node) is defs.Enum:
				decl_vars.extend(node.vars)

		return db, decl_vars, import_nodes

	def __pluck_imported(self, main: Module, imported: Module) -> SymbolDB:
		db: SymbolDB = {}
		for node in imported.entrypoint(Node).calculated():
			# FIXME 一旦Typesに限定
			if isinstance(node, (defs.Function, defs.Class, defs.Enum)):
				org_path = EntryPath.join(node.scope, node.symbol.to_string())
				path = EntryPath.join(main.path, org_path.relativefy(node.module.path).origin)
				db[path.origin] = node

		return db

	def __resolve_symbol(self, var: defs.AnnoAssign | defs.MoveAssign, db: SymbolDB) -> defs.Types:
		type_name = self.__resolve_type_name(var)
		candidates = [
			EntryPath.join(var.scope, type_name),
			EntryPath.join(var.module.path, type_name),
		]
		for candidate in candidates:
			if candidate.origin in db:
				return db[candidate.origin]

		raise ValueError(f'Unresolve var type symbol. symbol: {var.symbol.to_string()}')

	def __resolve_type_name(self, var: defs.AnnoAssign | defs.MoveAssign) -> str:
		if type(var) is defs.AnnoAssign:
			if var.var_type.is_a(defs.This) and var.symbol.to_string() == 'self':
				# XXX 名前空間末尾のクラス名を取る
				return EntryPath(var.namespace).last()[0]
			elif var.var_type.is_a(defs.Symbol):
				return var.var_type.to_string()
			else:
				return var.var_type.as_a(defs.GenericType).symbol.to_string()

		# XXX Unknownの名前は重要なので定数化などの方法で明示
		return 'Unknown'

# DB:
#   int: Class('$', 'int')
#   float: Class('$', 'float')
#   str: Class('$', 'str')
#   bool: Class('$', 'bool')
#   tuple: Class('$', 'tuple')
#   list: Class('$', 'list')
#   dict: Class('$', 'dict')
#   None: Class('$', 'None')
#   n: Var('n', var_type=ListType('int')) -> Class('n', 'list', value_type='int')
#   S: Class('S')
#   S.B: Class('S.B')
#   S.B.n: Var('S.B.n', var_type=Symbol('None')) -> Class('S.B.n', 'None')
#   S.A: Class('S.A')
#   S.A.n: Var('S.A.n', var_type=Symbol('int')) -> Class('S.A.n', 'int')
#   S.A.b: Class('S.A.b')
#   S.A.V: Class('S.A.V')
#   S.A.V.n: Var('S.A.V.n', var_type=Symbol('bool')) -> Class('S.A.V.n', 'bool')
#   S.A.func: Method('S.A.func')
#   S.A.func.self: Parameter('S.A.self') -> Var('S.A.self', var_type=Symbol('')) -> Class('S.A')
#   S.A.func.v: Parameter('S.A.v') -> Var('S.A.v', var_type=Symbol('V')) -> Class('S.A.V')
#   S.A.func.n: Var('S.A.func.n', var_type=Symbol('dict') -> Class('S.A.func.n', 'dict', key_type='str', value_type='int')
# Proc:
#   #1
#     scope: 'S.A.func', symbol: 'v.n', candidate: 'S.A.func.v', founded: Class('S.A.V'), recursive: scope: 'S.A.V', symbol: 'n'
#       -> scope: 'S.A.V', symbol: 'n', candidate: 'S.A.V.n', founded: Boolean('S.A.V.n')
#   #2
#     scope: 'S.A.func', symbol: 'S.A.n', candidate: 'S.A.func.S.A.n', founded: None
#     scope: 'S.A.func', symbol: 'S.A.n', candidate: 'S.A.n', founded: Integer('S.A.n')
#   #3
#     scope: 'S.A.func', symbol: 'n', candidate: 'S.A.func.n', founded: Dict('S.A.V.func.n')
#   #4
#     scope: 'S.A.func', symbol: 'self.n', candidate: 'S.A.func.self', founded: Class('S.A')
