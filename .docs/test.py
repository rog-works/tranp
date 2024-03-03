from abc import ABCMeta, abstractmethod
from typing import TypeVar


T = TypeVar('T')

class Node: ...
class Nodes:
	def by(self, full_path: str) -> Node:
		...

class Module:
	def node_by(self, full_path: str) -> Node: ...

class Modules:
	def module(self, module_path: str) -> Module: ...

class Raws(dict[str, T]): ...

class DB:
	raws: Raws['IReflection']

class IReflection(metaclass=ABCMeta):
	@property
	@abstractmethod
	def org_fullyname(self) -> str: ...

	@property
	@abstractmethod
	def origin(self) -> 'IReflection': ...

	@property
	@abstractmethod
	def attrs(self) -> list['IReflection']: ...

class Reflection(IReflection):
	def __init__(self, modules: Modules, db: DB) -> None:
		self._modules = modules
		self._raws = db.raws

	def node_by(self, full_path: str) -> Node: ...

class ReflectionOrigin(Reflection):
	def __init__(self, modules: Modules, db: DB, fullyname: str) -> None:
		super().__init__(modules, db)
		self._org_fullyname = fullyname

	@property
	def org_fullyname(self) -> str:
		return self._org_fullyname

	@property
	def origin(self) -> 'IReflection':
		return self._raws[self._org_fullyname]

	@property
	def attrs(self) -> list['IReflection']:
		return []

class ReflectionImport(ReflectionOrigin):
	def __init__(self, modules: Modules, db: DB, origin: IReflection) -> None:
		super().__init__(modules, db, origin.org_fullyname)
