from py2cpp.cpp.directive import pragma
from py2cpp.cpp.enum import CEnum

pragma('once')

class Vector:
	def __init__(self, x: float, y: float, z: float) -> None:
		self.x: float = x
		self.y: float = y
		self.z: float = z

class IntVector:
	def __init__(self, x: int, y: int, z: int) -> None:
		self.x: int = x
		self.y: int = y
		self.z: int = z

class CellMesh:
	# 面インデックス
	class FaceIndexs(CEnum):
		Left = 0
		Right = 1
		Back = 2
		Front = 3
		Bottom = 4
		Top = 5
		Max = 6

	@classmethod
	def fromCell(cls, cell: IntVector, unit: int = 100) -> Vector:
		return Vector(float(cell.x * unit), float(cell.y * unit), float(cell.z * unit))

	@classmethod
	def faceIndexToVector(cls, faceIndex: int) -> IntVector:
		map: dict[CellMesh.FaceIndexs, IntVector] = {
			CellMesh.FaceIndexs.Left: IntVector(-1, 0, 0),
			CellMesh.FaceIndexs.Right: IntVector(1, 0, 0),
			CellMesh.FaceIndexs.Back: IntVector(0, -1, 0),
			CellMesh.FaceIndexs.Front: IntVector(0, 1, 0),
			CellMesh.FaceIndexs.Bottom: IntVector(0, 0, -1),
			CellMesh.FaceIndexs.Top: IntVector(0, 0, 1),
		}
		return map[CellMesh.FaceIndexs(faceIndex)]
