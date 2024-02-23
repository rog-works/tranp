from typing import Callable, Iterator

from rogw.tranp.compatible.cpp.object import CObject

class Vector(CObject):
	def __init__(self, x: float, y: float, z: float) -> None:
		self.x: float = x
		self.y: float = y
		self.z: float = z

	def __add__(self, other: 'Vector | float | int') -> 'Vector':
		raise NotImplementedError()

	def __sub__(self, other: 'Vector | float | int') -> 'Vector':
		raise NotImplementedError()

class IntVector(CObject):
	def __init__(self, x: int, y: int, z: int) -> None:
		self.x: int = x
		self.y: int = y
		self.z: int = z

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

	def contains(self, location: Vector) -> bool:
		raise Exception('Not implemented')


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
