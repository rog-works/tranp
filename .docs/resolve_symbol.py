from py2cpp.ast.travarsal import EntryPath
from py2cpp.errors import LogicError
import py2cpp.node.definition as defs
from py2cpp.node.node import Node

n: list[int] = []

class S:
	class B:
		n: None = None

	class A:
		n: int = 0
		b: 'S.B'

		class V:
			n: bool = True

		def func(self, v: 'V') -> None:
			class Z: pass

			S.A.b.n
			n: dict[str, int] = {}
			print(f'{n}')
			print(f'{S.A.n}')
			print(f'{S.A.V.n}')
			print(f'{X.n}')
			print(f'{Z}')
			v.n
			self.n

class X:
	n: bool = True


def make_symbols(root: Node) -> dict[str, defs.Types]:
	db: dict[str, defs.Types] = {}
	for node in root.calculated():
		if isinstance(node, (defs.Function, defs.Class)):
			path = EntryPath.join(node.block.scope, node.symbol.to_string())
			db[path.origin] = node

	for _, node in db.items():
		for var in node.block.decl_vars:
			type_symbol = var.var_type.to_string()
			candidates = [
				EntryPath.join(var.scope, type_symbol),
				EntryPath.join(type_symbol),
			]
			path = EntryPath.join(node.block.scope, var.symbol.to_string())
			for candidate in candidates:
				if candidate.origin in db:
					db[path.origin] = db[candidate.origin]
					break

	return db


def resolve_symbol(scope: str, symbol: str, db: dict[str, defs.Types]) -> defs.Types | None:
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
	#   S.A.func.n: Var('S.A.func.n', type=DictType('str', 'int')) -> Class('S.A.func.n', 'dict', key_type='str', value_type='int')
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
	symbols = EntryPath(symbol)
	first, _ = symbols.first()[0]
	remain = symbols.shift(1)
	candidates = [
		EntryPath.join(scope, first),
		EntryPath.join(first),
	]
	for candidate in candidates:
		if candidate.origin in db:
			continue

		ctor = db[candidate.origin]
		if not remain.valid:
			return ctor

		founded = resolve_symbol(ctor.block.scope, remain.origin, db)
		if founded:
			return founded

	raise LogicError(f'Symbol not defined. scope: {scope}, symbol: {symbol}')
