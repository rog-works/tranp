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
	def need_cell_face_indexs(cls, need_cell_index: int) -> list[int]:
		"""必須セルに必要な6面インデックスを取得

		Args:
			need_cell_index (int): 必須セルインデックス
		Returns:
			list[int]: 6面インデックスリスト
		Note:
			needCells専用
		"""
		to_faces = {
			int(cls.NeedCellIndexs.Bottom0): [int(cls.FaceIndexs.Bottom), int(cls.FaceIndexs.Back)],
			int(cls.NeedCellIndexs.Bottom1): [int(cls.FaceIndexs.Bottom), int(cls.FaceIndexs.Left)],
			int(cls.NeedCellIndexs.Bottom2): [int(cls.FaceIndexs.Bottom), int(cls.FaceIndexs.Right)],
			int(cls.NeedCellIndexs.Bottom3): [int(cls.FaceIndexs.Bottom), int(cls.FaceIndexs.Front)],
			int(cls.NeedCellIndexs.Middle0): [int(cls.FaceIndexs.Back), int(cls.FaceIndexs.Left)],
			int(cls.NeedCellIndexs.Middle1): [int(cls.FaceIndexs.Back), int(cls.FaceIndexs.Right)],
			int(cls.NeedCellIndexs.Middle2): [int(cls.FaceIndexs.Front), int(cls.FaceIndexs.Left)],
			int(cls.NeedCellIndexs.Middle3): [int(cls.FaceIndexs.Front), int(cls.FaceIndexs.Right)],
			int(cls.NeedCellIndexs.Top0): [int(cls.FaceIndexs.Top), int(cls.FaceIndexs.Back)],
			int(cls.NeedCellIndexs.Top1): [int(cls.FaceIndexs.Top), int(cls.FaceIndexs.Left)],
			int(cls.NeedCellIndexs.Top2): [int(cls.FaceIndexs.Top), int(cls.FaceIndexs.Right)],
			int(cls.NeedCellIndexs.Top3): [int(cls.FaceIndexs.Top), int(cls.FaceIndexs.Front)],
		}
		return to_faces[need_cell_index]

	@classmethod
	def around_need_cell_face_indexs(cls, face_index: int) -> list[int]:
		"""
		6面方向の先のセルの周辺に存在する必須セルへの方向を示す6面インデックスを取得

		Args:
			face_index (int): 6面インデックス
		Returns:
			list[int]: 6面インデックスリスト
		Note:
			needCells専用
		"""
		to_faces = {
			int(cls.FaceIndexs.Left): [int(cls.FaceIndexs.Back), int(cls.FaceIndexs.Front), int(cls.FaceIndexs.Bottom), int(cls.FaceIndexs.Top)],
			int(cls.FaceIndexs.Right): [int(cls.FaceIndexs.Back), int(cls.FaceIndexs.Front), int(cls.FaceIndexs.Bottom), int(cls.FaceIndexs.Top)],
			int(cls.FaceIndexs.Back): [int(cls.FaceIndexs.Left), int(cls.FaceIndexs.Right), int(cls.FaceIndexs.Bottom), int(cls.FaceIndexs.Top)],
			int(cls.FaceIndexs.Front): [int(cls.FaceIndexs.Left), int(cls.FaceIndexs.Right), int(cls.FaceIndexs.Bottom), int(cls.FaceIndexs.Top)],
			int(cls.FaceIndexs.Bottom): [int(cls.FaceIndexs.Left), int(cls.FaceIndexs.Right), int(cls.FaceIndexs.Back), int(cls.FaceIndexs.Front)],
			int(cls.FaceIndexs.Top): [int(cls.FaceIndexs.Left), int(cls.FaceIndexs.Right), int(cls.FaceIndexs.Back), int(cls.FaceIndexs.Front)],
		}
		return to_faces[face_index]

	@classmethod
	def offset_cell_to_face_index(cls, offset_cell: IntVector) -> int:
		"""
		オフセットセル座標(3x3x3)を6面インデックスに変換

		Args:
			offset_cell (IntVector): オフセットセル座標(3x3x3)
		Returns:
			int: 6面インデックス
		"""
		offset_index = cls.offset_cell_to_index(offset_cell)
		to_faces = {
			int(cls.OffsetIndexs.Left): int(cls.FaceIndexs.Left),
			int(cls.OffsetIndexs.Right): int(cls.FaceIndexs.Right),
			int(cls.OffsetIndexs.Back): int(cls.FaceIndexs.Back),
			int(cls.OffsetIndexs.Front): int(cls.FaceIndexs.Front),
			int(cls.OffsetIndexs.Bottom): int(cls.FaceIndexs.Bottom),
			int(cls.OffsetIndexs.Top): int(cls.FaceIndexs.Top),
		}
		if offset_index not in to_faces:
			print('Fatal Error! offset_index: %d', offset_index)
			return 0

		return to_faces[offset_index]

	@classmethod
	def face_index_to_vector(cls, face_index: int) -> IntVector:
		"""6面インデックスからベクトルに変換

		Args:
			face_index (int): 6面インデックス
		Returns:
			IntVector: ベクトル
		"""
		to_vector: dict[CellMesh.FaceIndexs, IntVector] = {
			CellMesh.FaceIndexs.Left: IntVector(-1, 0, 0),
			CellMesh.FaceIndexs.Right: IntVector(1, 0, 0),
			CellMesh.FaceIndexs.Back: IntVector(0, -1, 0),
			CellMesh.FaceIndexs.Front: IntVector(0, 1, 0),
			CellMesh.FaceIndexs.Bottom: IntVector(0, 0, -1),
			CellMesh.FaceIndexs.Top: IntVector(0, 0, 1),
		}
		return to_vector[CellMesh.FaceIndexs(face_index)]

	@classmethod
	def invert_face_index(cls, face_index: int) -> int:
		"""6面インデックスを反転

		Args:
			face_index (int): 6面インデックス
		Returns:
			int: 反転した6面インデックス
		"""
		to_faces = {
			int(cls.FaceIndexs.Left): int(cls.FaceIndexs.Right),
			int(cls.FaceIndexs.Right): int(cls.FaceIndexs.Left),
			int(cls.FaceIndexs.Back): int(cls.FaceIndexs.Front),
			int(cls.FaceIndexs.Front): int(cls.FaceIndexs.Back),
			int(cls.FaceIndexs.Bottom): int(cls.FaceIndexs.Top),
			int(cls.FaceIndexs.Top): int(cls.FaceIndexs.Bottom),
		}
		return to_faces[face_index]

	@classmethod
	def face_box_to_face_index(cls, face_box: Box3d, unit: int) -> int:
		"""面のバウンドボックスから6面インデックスに変換

		Args:
			face_box (Box3d): 面のバウンドボックス
			unit (int): 単位
		Returns:
			int: 6面インデックス
		"""
		cell_center_location = face_box.min + unit / 2
		cell = cls.to_cell(cell_center_location, unit)
		cell_base_location = cls.from_cell(cell, unit)
		face_size = face_box.max - face_box.min
		face_offset_location = face_box.min - cell_base_location
		face_center_location = (face_offset_location + face_size) * 3 / 2
		face_offset = cls.to_cell(face_center_location, unit)
		face_index = cls.offset_cell_to_face_index(face_offset)
		print('cell: (%d, %d, %d), face_offset: (%d, %d, %d), face_size: (%.2f, %.2f, %.2f), cell_base_location: (%.2f, %.2f, %.2f), cell_center_location: (%.2f, %.2f, %.2f), face_offset_location: (%.2f, %.2f, %.2f), face_center_location: (%.2f, %.2f, %.2f), result: %d', cell.x, cell.y, cell.z, face_offset.x, face_offset.y, face_offset.z, face_size.x, face_size.y, face_size.z, cell_base_location.x, cell_base_location.y, cell_base_location.z, cell_center_location.x, cell_center_location.y, cell_center_location.z, face_offset_location.x, face_offset_location.y, face_offset_location.z, face_center_location.x, face_center_location.y, face_center_location.z, face_index)
		return face_index

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
	def to_polygon_boxs(cls, cell_box: Box3d, unit: int) -> list[Box3d]:
		"""セルの6面を囲うバウンドボックスを取得
		囲うために実際のバウンドボックスより10%大きいサイズになる点に注意

		Args:
			coll_box (Box3d): セルのバウンドボックス
			unit (int): 単位
		Returns:
			list[Box3d]: 面毎のバウンドボックスリスト
		"""
		offset = unit / 10
		min = cell_box.min
		max = cell_box.max
		return [
			Box3d(Vector(min.x - offset, min.y - offset, min.z - offset), Vector(min.x + offset, max.y + offset, max.z + offset)),
			Box3d(Vector(max.x - offset, min.y - offset, min.z - offset), Vector(max.x + offset, max.y + offset, max.z + offset)),
			Box3d(Vector(min.x - offset, min.y - offset, min.z - offset), Vector(max.x + offset, min.y + offset, max.z + offset)),
			Box3d(Vector(min.x - offset, max.y - offset, min.z - offset), Vector(max.x + offset, max.y + offset, max.z + offset)),
			Box3d(Vector(min.x - offset, min.y - offset, min.z - offset), Vector(max.x + offset, max.y + offset, min.z + offset)),
			Box3d(Vector(min.x - offset, min.y - offset, max.z - offset), Vector(max.x + offset, max.y + offset, max.z + offset)),
		]

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
