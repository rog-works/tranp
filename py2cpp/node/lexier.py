import py2cpp.node.definition as defs
from py2cpp.node.node import Node


class Lexier:
	def resolve(self, symbol: defs.Symbol) -> Node:
		...


	def is_type(self, symbol: defs.Symbol) -> bool:
		return self.resolve(symbol).is_a(defs.Class) or self.resolve(symbol).is_a(defs.Enum)


	def is_var(self, symbol: defs.Symbol) -> bool:
		return self.resolve(symbol).is_a(defs.Variable)
	
