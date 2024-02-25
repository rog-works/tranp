from typing import Callable, Iterator

from rogw.tranp.compatible.cpp.object import CObject, CRef

class Vector(CObject):
	def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
		self.x: float = x
		self.y: float = y
		self.z: float = z

	def __add__(self, other: 'Vector | float | int') -> 'Vector':
		raise NotImplementedError()

	def __sub__(self, other: 'Vector | float | int') -> 'Vector':
		raise NotImplementedError()

	def __mul__(self, other: 'Vector | float | int') -> 'Vector':
		raise NotImplementedError()

	def __truediv__(self, other: 'Vector | float | int') -> 'Vector':
		raise NotImplementedError()

class IntVector(CObject):
	def __init__(self, x: int = 0, y: int = 0, z: int = 0) -> None:
		self.x: int = x
		self.y: int = y
		self.z: int = z

	def __add__(self, other: 'IntVector | float | int') -> 'IntVector':
		raise NotImplementedError()

	def __sub__(self, other: 'IntVector | float | int') -> 'IntVector':
		raise NotImplementedError()

class IntVector2(CObject):
	def __init__(self, x: int = 0, y: int = 0) -> None:
		self.x: int = x
		self.y: int = y

	def __add__(self, other: 'IntVector | float | int') -> 'IntVector':
		raise NotImplementedError()

	def __sub__(self, other: 'IntVector | float | int') -> 'IntVector':
		raise NotImplementedError()

class Box3d(CObject):
	"""3Dレンジオブジェクト

	Attributes:
		min (Vector): 開始座標
		max (Vector): 終了座標
	"""

	def __init__(self, min: Vector, max: Vector) -> None:
		"""インスタンスを生成

		Args:
			min (Vector): 開始座標
			max (Vector): 終了座標
		"""
		self.min: Vector = min
		self.max: Vector = max

	def contains(self, location: 'Vector | Box3d') -> bool:
		raise Exception('Not implemented')


class MeshRaw(CObject):
	def vertex_indices_itr(self) -> Iterator[int]:
		raise NotImplementedError()

	def triangle_indices_itr(self) -> Iterator[int]:
		raise NotImplementedError()

	def is_vertex(self, index: int) -> bool:
		raise NotImplementedError()

	def is_triangle(self, index: int) -> bool:
		raise NotImplementedError()

	def get_vertex(self, index: int) -> Vector:
		raise NotImplementedError()

	def get_tri_bounds(self, index: int) -> Box3d:
		raise NotImplementedError()

	def clear(self) -> None:
		raise NotImplementedError()

class Mesh(CObject):
	def process_mesh(self, callback: Callable[[MeshRaw[CRef]], None]) -> None:
		raise NotImplementedError()

	def edit_mesh(self, callback: Callable[[MeshRaw[CRef]], None]) -> None:
		raise NotImplementedError()
