from typing import Callable, Iterator

from rogw.tranp.compatible.cpp.object import CP, CRef, CRefConst

class Vector:
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

class Vector2:
	def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
		self.x: float = x
		self.y: float = y

	def __add__(self, other: 'Vector2 | float | int') -> 'Vector2':
		raise NotImplementedError()

	def __sub__(self, other: 'Vector2 | float | int') -> 'Vector2':
		raise NotImplementedError()

	def __mul__(self, other: 'Vector2 | float | int') -> 'Vector2':
		raise NotImplementedError()

	def __truediv__(self, other: 'Vector2 | float | int') -> 'Vector2':
		raise NotImplementedError()

class IntVector:
	def __init__(self, x: int = 0, y: int = 0, z: int = 0) -> None:
		self.x: int = x
		self.y: int = y
		self.z: int = z

	def __add__(self, other: 'IntVector | float | int') -> 'IntVector':
		raise NotImplementedError()

	def __sub__(self, other: 'IntVector | float | int') -> 'IntVector':
		raise NotImplementedError()

class IntVector2:
	def __init__(self, x: int = 0, y: int = 0) -> None:
		self.x: int = x
		self.y: int = y

	def __add__(self, other: 'IntVector2 | float | int') -> 'IntVector2':
		raise NotImplementedError()

	def __sub__(self, other: 'IntVector2 | float | int') -> 'IntVector2':
		raise NotImplementedError()

class Box3d:
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

class UV:
	def append_element(self, uv: Vector2) -> int:
		raise NotImplementedError()

	def set_triangle(self, polygon_index: int, uv_ids: IntVector, enable: bool) -> None:
		raise NotImplementedError()

class Attributes:
	def num_uv_layers(self) -> int:
		raise NotImplementedError()

	def primary_uv(self) -> CP[UV]:
		raise NotImplementedError()

	def set_num_uv_layers(self, num: int) -> None:
		raise NotImplementedError()

class MeshRaw:
	# Vertex ----------

	def is_vertex(self, index: int) -> bool:
		raise NotImplementedError()

	def vertex_indices_itr(self) -> Iterator[int]:
		raise NotImplementedError()

	def get_vertex(self, index: int) -> Vector:
		raise NotImplementedError()

	def append_vertex(self, vector: Vector) -> int:
		raise NotImplementedError()

	# Triangle ----------

	def is_triangle(self, index: int) -> bool:
		raise NotImplementedError()

	def triangle_indices_itr(self) -> Iterator[int]:
		raise NotImplementedError()

	def get_tri_bounds(self, index: int) -> Box3d:
		raise NotImplementedError()

	def append_triangle(self, vertex_ids: IntVector) -> int:
		raise NotImplementedError()

	def remove_triangle(self, index: int) -> None:
		raise NotImplementedError()

	# Triangle Group ----------

	def has_triangle_groups(self) -> bool:
		raise NotImplementedError()

	def max_group_id(self) -> int:
		raise NotImplementedError()

	def enable_triangle_groups(self, index: int) -> None:
		raise NotImplementedError()

	def set_triangle_group(self, polygon_index: int, group_index: int) -> None:
		raise NotImplementedError()

	# Attributes ----------

	def has_attributes(self) -> bool:
		raise NotImplementedError()

	def enable_attributes(self) -> None:
		raise NotImplementedError()

	def attributes(self) -> Attributes:
		raise NotImplementedError()

	# Common ----------

	def clear(self) -> None:
		raise NotImplementedError()

class Mesh:
	def process_mesh(self, callback: Callable[[CRef[MeshRaw]], None] | Callable[[CRefConst[MeshRaw]], None]) -> None:
		raise NotImplementedError()

	def edit_mesh(self, callback: Callable[[CRef[MeshRaw]], None] | Callable[[CRefConst[MeshRaw]], None]) -> None:
		raise NotImplementedError()
