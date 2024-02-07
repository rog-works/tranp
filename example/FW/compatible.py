from typing import Callable, Iterator

from py2cpp.compatible.cpp.object import CObject

class Vector(CObject):
	def __init__(self, x: float, y: float, z: float) -> None:
		self.x: float = x
		self.y: float = y
		self.z: float = z

	def __add__(self, other: 'Vector | float') -> 'Vector':
		raise NotImplementedError()

	def __sub__(self, other: 'Vector | float') -> 'Vector':
		raise NotImplementedError()

class IntVector(CObject):
	def __init__(self, x: int, y: int, z: int) -> None:
		self.x: int = x
		self.y: int = y
		self.z: int = z

	def __add__(self, other: 'IntVector | float') -> 'IntVector':
		raise NotImplementedError()

	def __sub__(self, other: 'IntVector | float') -> 'IntVector':
		raise NotImplementedError()

class MeshRaw(CObject):
	def vertex_indices_itr(self) -> Iterator[int]:
		raise NotImplementedError()

	def is_vertex(self, index: int) -> bool:
		raise NotImplementedError()

	def get_vertex(self, index: int) -> Vector:
		raise NotImplementedError()

class Mesh(CObject):
	def process_mesh(self, callback: Callable[[MeshRaw], None]) -> None:
		raise NotImplementedError()
