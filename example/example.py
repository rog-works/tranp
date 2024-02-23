from rogw.tranp.compatible.cpp.object import CP, CConst, CRef
from rogw.tranp.compatible.cpp.preprocess import directive
from rogw.tranp.compatible.cpp.enum import CEnum

directive('#pragma once')

from example.FW.compatible import Box3d, IntVector, Mesh, MeshRaw, Vector

class CellMesh:
	"""セル(メッシュ)関連のライブラリー"""

	class VertexIndexs(CEnum):
		"""セルの8頂点インデックス"""
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
		"""セルの6面インデックス"""
		Left = 0
		Right = 1
		Back = 2
		Front = 3
		Bottom = 4
		Top = 5
		Max = 6

	class OffsetIndexs(CEnum):
		"""オフセットインデックス(3x3x3)"""
		Left = 12
		Right = 14
		Back = 10
		Front = 16
		Bottom = 4
		Top = 22
		Max = 27

	class NeedCellIndexs(CEnum):
		"""必須セルインデックス @note needCells専用"""
		Bottom0 = 0
		Bottom1 = 1
		Bottom2 = 2
		Bottom3 = 3
		Middle0 = 4
		Middle1 = 5
		Middle2 = 6
		Middle3 = 7
		Top0 = 8
		Top1 = 9
		Top2 = 10
		Top3 = 11
		Max = 12

	@classmethod
	def to_cell(cls, location: Vector, unit: int = 100) -> IntVector:
		"""セル座標に変換

		Args:
			location (FVector): 座標
			unit (int): 単位(default = 100cm)
		Returns:
			FIntVector: セル座標
		Note:
			単位の倍数に近い座標で変換を行うのは不正確になり得るため注意が必要
		"""
		cell = IntVector(int(location.x), int(location.y), int(location.z))
		return IntVector(
			int(cell.x / unit) + (-1 if location.x < 0 else 0),
			int(cell.y / unit) + (-1 if location.y < 0 else 0),
			int(cell.z / unit) + (-1 if location.z < 0 else 0)
		)

	@classmethod
	def from_cell(cls, cell: IntVector, unit: int = 100) -> Vector:
		"""セル座標を座標に変換

		Args:
			cell (FIntVector): セル座標
			unit (int): 単位(default = 100cm)
		Returns:
			FVector: 座標
		"""
		return Vector(float(cell.x * unit), float(cell.y * unit), float(cell.z * unit))

	@classmethod
	def to_center(cls, location: Vector, unit: int = 100) -> Vector:
		""" 座標からセルの中心座標に変換

		Args:
			location (Vector): 座標
			unit (int): 単位(default = 100cm)
		Returns:
			Vector: セルの中心座標
		Note:
			単位の倍数に近い座標で変換を行うのは不正確になり得るため注意が必要
		"""
		based = cls.from_cell(cls.to_cell(location, unit), unit)
		return based + int(unit / 2)

	@classmethod
	def offset_cell_to_index(cls, offset_cell: IntVector) -> int:
		"""オフセットセル座標(3x3x3)をオフセットインデックスに変換

		Args:
			offset_cell (IntVector): オフセットセル座標(3x3x3)
		Returns:
			int: オフセットインデックス(3x3x3)
		"""
		return offset_cell.z * 9 + offset_cell.y * 3 + offset_cell.x

	@classmethod
	def offset_index_to_cell(cls, offset_index: int) -> IntVector:
		"""オフセットインデックス(3x3x3)からオフセットセル座標に変換

		Args:
			offset_index (int): オフセットインデックス(3x3x3)
		Returns:
			IntVector: オフセットセル座標(3x3x3)
		"""
		x = int(offset_index % 3)
		y = int(offset_index % 9 / 3)
		z = int(offset_index / 9)
		return IntVector(x, y, z)

	@classmethod
	def face_index_to_vector(cls, face_index: int) -> IntVector:
		"""6面インデックスからベクトルに変換

		Args:
			face_index (int): 6面インデックス
		Returns:
			FIntVector: ベクトル
		"""
		map: dict[CellMesh.FaceIndexs, IntVector] = {
			CellMesh.FaceIndexs.Left: IntVector(-1, 0, 0),
			CellMesh.FaceIndexs.Right: IntVector(1, 0, 0),
			CellMesh.FaceIndexs.Back: IntVector(0, -1, 0),
			CellMesh.FaceIndexs.Front: IntVector(0, 1, 0),
			CellMesh.FaceIndexs.Bottom: IntVector(0, 0, -1),
			CellMesh.FaceIndexs.Top: IntVector(0, 0, 1),
		}
		return map[CellMesh.FaceIndexs(face_index)]

	@classmethod
	def to_cell_box(cls, cell: IntVector, unit: int) -> Box3d:
		"""セルのバウンドボックスを取得

		Args:
			cell (IntVector): セル座標
			unit (int): 単位
		Returns:
			Box3d: バウンドボックス
		"""
		min_location = cls.from_cell(cell, unit)
		max_location = cls.from_cell(cell + IntVector(1, 1, 1), unit)
		return Box3d(min_location, max_location)

	@classmethod
	def to_vertex_boxs(cls, cell_box: Box3d, unit: int) -> list[Box3d]:
		"""セルの8頂点を囲うバウンドボックスを取得

		Args:
			coll_box (Box3d): セルのバウンドボックス
			unit (int): 単位
		Returns:
			list[Box3d]: 頂点毎のバウンドボックスリスト
		"""
		offset = unit / 10.0
		min = cell_box.min
		max = cell_box.max
		positions = [
			Vector(min.x, min.y, min.z),
			Vector(max.x, min.y, min.z),
			Vector(max.x, max.y, min.z),
			Vector(min.x, max.y, min.z),
			Vector(min.x, min.y, max.z),
			Vector(max.x, min.y, max.z),
			Vector(max.x, max.y, max.z),
			Vector(min.x, max.y, max.z),
		]
		return [Box3d(position - offset,  position + offset) for position in positions]

	@classmethod
	def by_vertex_ids(cls, mesh: Mesh[CP], cell: IntVector, unit: int) -> list[int]:
		"""セルの8頂点の頂点IDを取得する

		Args:
			mesh (*Mesh): ダイナミックメッシュ
			cell (IntVector): セル座標
			unit (int): 単位
		Returns:
			list[int]: 頂点IDリスト
		"""
		outIds = [-1, -1, -1, -1, -1, -1, -1, -1]
		def closure(origin: MeshRaw[CRef, CConst]) -> None:
			cellBox = cls.to_cell_box(cell, unit)
			boxs = cls.to_vertex_boxs(cellBox, unit)
			for i, box in enumerate(boxs):
				for vi in origin.vertex_indices_itr():
					# 実体がない(参照カウント0)インデックスを除外
					if not origin.is_vertex(vi):
						continue

					v = origin.get_vertex(vi)
					if box.contains(v):
						outIds[i] = vi
						break

		mesh.process_mesh(closure)

		return outIds
