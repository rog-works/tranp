from py2cpp.compatible.cpp.preprocess import directive
from py2cpp.compatible.cpp.enum import CEnum
from py2cpp.compatible.cpp.object import CObject, CP, CSP, CConst

directive('#pragma once')

from example.FW.compatible import IntVector, Vector, Mesh, MeshRaw

class Box3d(CObject):
	def __init__(self, min: Vector, max: Vector) -> None:
		self.min: Vector = min
		self.max: Vector = max

	def contains(self, location: Vector) -> bool:
		raise NotImplementedError()

class CellMesh:
	class VertexIndexs(CEnum):
		BottomBackLeft = 0
		BottomBackRight = 1
		BottomFrontLeft = 2
		BottomFrontRight = 3
		TopBackLeft = 4
		TopBackRight = 5
		TopFrontLeft = 6
		TopFrontRight = 7
		Max = 8

	class FaceIndexs(CEnum):
		Left = 0
		Right = 1
		Back = 2
		Front = 3
		Bottom = 4
		Top = 5
		Max = 6

	@classmethod
	def from_cell(cls, cell: IntVector, unit: int = 100) -> Vector:
		cell.x = cell.x * unit
		cell.y = cell.y * unit
		cell.z = cell.z * unit
		fx = float(cell.x)
		fy = float(cell.y)
		fz = float(cell.z)
		print('%f, %f, %f', fx, fy, fz)
		return Vector(fx, fy, fz)

	@classmethod
	def face_index_to_vector(cls, faceIndex: int) -> IntVector:
		map: dict[CellMesh.FaceIndexs, IntVector] = {
			CellMesh.FaceIndexs.Left: IntVector(-1, 0, 0),
			CellMesh.FaceIndexs.Right: IntVector(1, 0, 0),
			CellMesh.FaceIndexs.Back: IntVector(0, -1, 0),
			CellMesh.FaceIndexs.Front: IntVector(0, 1, 0),
			CellMesh.FaceIndexs.Bottom: IntVector(0, 0, -1),
			CellMesh.FaceIndexs.Top: IntVector(0, 0, 1),
		}
		return map[CellMesh.FaceIndexs(faceIndex)]

	@classmethod
	def to_cell_box(cls, cell: IntVector, unit: int) -> Box3d[CSP, CConst]:
		minLocation = cls.from_cell(cell, unit)
		maxLocation = cls.from_cell(cell + IntVector(1, 1, 1), unit)
		return Box3d(minLocation, maxLocation)

	@classmethod
	def to_vertex_boxs(cls, cellBox: Box3d[CP], unit: int) -> list[Box3d]:
		offset = unit / 10
		min = cellBox.min
		max = cellBox.max
		positions: list[Vector] = [
			Vector(min.x, min.y, min.z),
			Vector(max.x, min.y, min.z),
			Vector(max.x, max.y, min.z),
			Vector(min.x, max.y, min.z),
			Vector(min.x, min.y, max.z),
			Vector(max.x, min.y, max.z),
			Vector(max.x, max.y, max.z),
			Vector(min.x, max.y, max.z),
		]
		out: list[Box3d] = []
		for position in positions:
			out.append(Box3d(position - offset,  position + offset))

		return out

	@classmethod
	def by_vertex_ids(cls, mesh: Mesh, cell: IntVector, unit: int) -> list[int]:
		outIds: list[int] = [-1, -1, -1, -1, -1, -1, -1, -1]
		def closure(origin: MeshRaw) -> None:
			cellBox = cls.to_cell_box(cell, unit)
			boxs = cls.to_vertex_boxs(cellBox, unit)
			for i in range(int(CellMesh.VertexIndexs.Max)):
				box = boxs[i]
				for vi in origin.vertex_indices_itr():
					if not origin.is_vertex(vi):
						continue

					v = origin.get_vertex(vi)
					if box.contains(v):
						outIds[i] = vi
						break

		mesh.process_mesh(closure)

		return outIds
