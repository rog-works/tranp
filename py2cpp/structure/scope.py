from py2cpp.node.node import Node


class Scope:
	""" @deprecated """

	def __init__(self, parent: 'Scope' | None, holder: Node) -> None:
		self.__parent = parent
		self.__holder = holder
		self.__namespace_nest = 0 if parent is None else parent.nest


	@property
	def holder(self) -> Node:
		return self.__holder


	@property
	def namespace(self) -> Node:
		if self.__parent is None or self.__parent.__holder is self.__holder:
			return self.__holder
		else:
			return self.__parent.__holder


	@property
	def nest(self) -> int:
		if self.__parent is None or self.__parent.__holder is self.__holder:
			return self.__namespace_nest
		else:
			return self.__parent.nest + 1


class ScopeStack:
	""" @deprecated """

	def __init__(self) -> None:
		self.__scopes: list[Scope]


	@property
	def peek(self) -> Scope:
		return self.__scopes[-1]


	def push(self, holder: Node) -> None:
		self.__scopes.append(Scope(self.peek, holder))


	def pop(self, holder: Node) -> Scope:
		if self.peek.holder != holder:
			raise ValueError()

		return self.__scopes.pop()
