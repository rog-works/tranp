// #include "rogw/tranp/compatible/cpp/object.h"
// #include "rogw/tranp/compatible/cpp/preprocess.h"
// #include "rogw/tranp/compatible/cpp/enum.h"
#pragma once
#include "example/FW/compatible.h"
/**
 * セル(メッシュ)関連のライブラリー
 */
class CellMesh {
	/**
	 * セルの8頂点インデックス
	 */
	public: enum class VertexIndexs {
		BottomBackLeft = 0,
		BottomBackRight = 1,
		BottomFrontLeft = 2,
		BottomFrontRight = 3,
		TopBackLeft = 4,
		TopBackRight = 5,
		TopFrontLeft = 6,
		TopFrontRight = 7,
		Max = 8,
	};
	/**
	 * セルの6面インデックス
	 */
	public: enum class FaceIndexs {
		Left = 0,
		Right = 1,
		Back = 2,
		Front = 3,
		Bottom = 4,
		Top = 5,
		Max = 6,
	};
	/**
	 * オフセットインデックス(3x3x3)
	 */
	public: enum class OffsetIndexs {
		Left = 12,
		Right = 14,
		Back = 10,
		Front = 16,
		Bottom = 4,
		Top = 22,
		Max = 27,
	};
	/**
	 * 必須セルインデックス @note needCells専用
	 */
	public: enum class NeedCellIndexs {
		Bottom0 = 0,
		Bottom1 = 1,
		Bottom2 = 2,
		Bottom3 = 3,
		Middle0 = 4,
		Middle1 = 5,
		Middle2 = 6,
		Middle3 = 7,
		Top0 = 8,
		Top1 = 9,
		Top2 = 10,
		Top3 = 11,
		Max = 12,
	};
	/**
	 * セル座標に変換
	 * @param location 座標
	 * @param unit 単位(default = 100cm)
	 * @return セル座標
	 * @note 単位の倍数に近い座標で変換を行うのは不正確になり得るため注意が必要
	 */
	public: static IntVector to_cell(Vector location, int unit = 100) {
		IntVector cell = IntVector((int)(location.x), (int)(location.y), (int)(location.z));
		return IntVector((int)(cell.x / unit) + (location.x < 0 ? -1 : 0), (int)(cell.y / unit) + (location.y < 0 ? -1 : 0), (int)(cell.z / unit) + (location.z < 0 ? -1 : 0));
	}
	/**
	 * セル座標を座標に変換
	 * @param cell セル座標
	 * @param unit 単位(default = 100cm)
	 * @return 座標
	 */
	public: static Vector from_cell(IntVector cell, int unit = 100) {
		return Vector((float)(cell.x * unit), (float)(cell.y * unit), (float)(cell.z * unit));
	}
	/**
	 * 座標からセルの中心座標に変換
	 * @param location 座標
	 * @param unit 単位(default = 100cm)
	 * @return セルの中心座標
	 * @note 単位の倍数に近い座標で変換を行うのは不正確になり得るため注意が必要
	 */
	public: static Vector to_center(Vector location, int unit = 100) {
		Vector based = CellMesh::from_cell(CellMesh::to_cell(location, unit), unit);
		return based + (int)(unit / 2);
	}
	/**
	 * オフセットセル座標(3x3x3)をオフセットインデックスに変換
	 * @param offset_cell オフセットセル座標(3x3x3)
	 * @return オフセットインデックス(3x3x3)
	 */
	public: static int offset_cell_to_index(IntVector offset_cell) {
		return offset_cell.z * 9 + offset_cell.y * 3 + offset_cell.x;
	}
	/**
	 * オフセットインデックス(3x3x3)からオフセットセル座標に変換
	 * @param offset_index オフセットインデックス(3x3x3)
	 * @return オフセットセル座標(3x3x3)
	 */
	public: static IntVector offset_index_to_cell(int offset_index) {
		int x = (int)(offset_index % 3);
		int y = (int)(offset_index % 9 / 3);
		int z = (int)(offset_index / 9);
		return IntVector(x, y, z);
	}
	/**
	 * 必須セルに必要な6面インデックスを取得
	 * @param need_cell_index 必須セルインデックス
	 * @return 6面インデックスリスト
	 * @note needCells専用
	 */
	public: static std::vector<int> need_cell_face_indexs(int need_cell_index) {
		std::map<int, std::vector<int>> to_faces = {
			{(int)(CellMesh::NeedCellIndexs::Bottom0), {
			{(int)(CellMesh::FaceIndexs::Bottom)},
			{(int)(CellMesh::FaceIndexs::Back)},
		}},
			{(int)(CellMesh::NeedCellIndexs::Bottom1), {
			{(int)(CellMesh::FaceIndexs::Bottom)},
			{(int)(CellMesh::FaceIndexs::Left)},
		}},
			{(int)(CellMesh::NeedCellIndexs::Bottom2), {
			{(int)(CellMesh::FaceIndexs::Bottom)},
			{(int)(CellMesh::FaceIndexs::Right)},
		}},
			{(int)(CellMesh::NeedCellIndexs::Bottom3), {
			{(int)(CellMesh::FaceIndexs::Bottom)},
			{(int)(CellMesh::FaceIndexs::Front)},
		}},
			{(int)(CellMesh::NeedCellIndexs::Middle0), {
			{(int)(CellMesh::FaceIndexs::Back)},
			{(int)(CellMesh::FaceIndexs::Left)},
		}},
			{(int)(CellMesh::NeedCellIndexs::Middle1), {
			{(int)(CellMesh::FaceIndexs::Back)},
			{(int)(CellMesh::FaceIndexs::Right)},
		}},
			{(int)(CellMesh::NeedCellIndexs::Middle2), {
			{(int)(CellMesh::FaceIndexs::Front)},
			{(int)(CellMesh::FaceIndexs::Left)},
		}},
			{(int)(CellMesh::NeedCellIndexs::Middle3), {
			{(int)(CellMesh::FaceIndexs::Front)},
			{(int)(CellMesh::FaceIndexs::Right)},
		}},
			{(int)(CellMesh::NeedCellIndexs::Top0), {
			{(int)(CellMesh::FaceIndexs::Top)},
			{(int)(CellMesh::FaceIndexs::Back)},
		}},
			{(int)(CellMesh::NeedCellIndexs::Top1), {
			{(int)(CellMesh::FaceIndexs::Top)},
			{(int)(CellMesh::FaceIndexs::Left)},
		}},
			{(int)(CellMesh::NeedCellIndexs::Top2), {
			{(int)(CellMesh::FaceIndexs::Top)},
			{(int)(CellMesh::FaceIndexs::Right)},
		}},
			{(int)(CellMesh::NeedCellIndexs::Top3), {
			{(int)(CellMesh::FaceIndexs::Top)},
			{(int)(CellMesh::FaceIndexs::Front)},
		}},
		};
		return to_faces[need_cell_index];
	}
	/**
	 * 6面方向の先のセルの周辺に存在する必須セルへの方向を示す6面インデックスを取得
	 * @param face_index 6面インデックス
	 * @return 6面インデックスリスト
	 * @note needCells専用
	 */
	public: static std::vector<int> around_need_cell_face_indexs(int face_index) {
		std::map<int, std::vector<int>> to_faces = {
			{(int)(CellMesh::FaceIndexs::Left), {
			{(int)(CellMesh::FaceIndexs::Back)},
			{(int)(CellMesh::FaceIndexs::Front)},
			{(int)(CellMesh::FaceIndexs::Bottom)},
			{(int)(CellMesh::FaceIndexs::Top)},
		}},
			{(int)(CellMesh::FaceIndexs::Right), {
			{(int)(CellMesh::FaceIndexs::Back)},
			{(int)(CellMesh::FaceIndexs::Front)},
			{(int)(CellMesh::FaceIndexs::Bottom)},
			{(int)(CellMesh::FaceIndexs::Top)},
		}},
			{(int)(CellMesh::FaceIndexs::Back), {
			{(int)(CellMesh::FaceIndexs::Left)},
			{(int)(CellMesh::FaceIndexs::Right)},
			{(int)(CellMesh::FaceIndexs::Bottom)},
			{(int)(CellMesh::FaceIndexs::Top)},
		}},
			{(int)(CellMesh::FaceIndexs::Front), {
			{(int)(CellMesh::FaceIndexs::Left)},
			{(int)(CellMesh::FaceIndexs::Right)},
			{(int)(CellMesh::FaceIndexs::Bottom)},
			{(int)(CellMesh::FaceIndexs::Top)},
		}},
			{(int)(CellMesh::FaceIndexs::Bottom), {
			{(int)(CellMesh::FaceIndexs::Left)},
			{(int)(CellMesh::FaceIndexs::Right)},
			{(int)(CellMesh::FaceIndexs::Back)},
			{(int)(CellMesh::FaceIndexs::Front)},
		}},
			{(int)(CellMesh::FaceIndexs::Top), {
			{(int)(CellMesh::FaceIndexs::Left)},
			{(int)(CellMesh::FaceIndexs::Right)},
			{(int)(CellMesh::FaceIndexs::Back)},
			{(int)(CellMesh::FaceIndexs::Front)},
		}},
		};
		return to_faces[face_index];
	}
	/**
	 * オフセットセル座標(3x3x3)を6面インデックスに変換
	 * @param offset_cell オフセットセル座標(3x3x3)
	 * @return 6面インデックス
	 */
	public: static int offset_cell_to_face_index(IntVector offset_cell) {
		int offset_index = CellMesh::offset_cell_to_index(offset_cell);
		std::map<int, int> to_faces = {
			{(int)(CellMesh::OffsetIndexs::Left), (int)(CellMesh::FaceIndexs::Left)},
			{(int)(CellMesh::OffsetIndexs::Right), (int)(CellMesh::FaceIndexs::Right)},
			{(int)(CellMesh::OffsetIndexs::Back), (int)(CellMesh::FaceIndexs::Back)},
			{(int)(CellMesh::OffsetIndexs::Front), (int)(CellMesh::FaceIndexs::Front)},
			{(int)(CellMesh::OffsetIndexs::Bottom), (int)(CellMesh::FaceIndexs::Bottom)},
			{(int)(CellMesh::OffsetIndexs::Top), (int)(CellMesh::FaceIndexs::Top)},
		};
		if ((!to_faces.contains(offset_index))) {
			printf("Fatal Error! offset_index: %d", offset_index);
			return 0;
		}
		return to_faces[offset_index];
	}
	/**
	 * 6面インデックスからベクトルに変換
	 * @param face_index 6面インデックス
	 * @return ベクトル
	 */
	public: static IntVector face_index_to_vector(int face_index) {
		std::map<CellMesh::FaceIndexs, IntVector> to_vector = {
			{CellMesh::FaceIndexs::Left, IntVector(-1, 0, 0)},
			{CellMesh::FaceIndexs::Right, IntVector(1, 0, 0)},
			{CellMesh::FaceIndexs::Back, IntVector(0, -1, 0)},
			{CellMesh::FaceIndexs::Front, IntVector(0, 1, 0)},
			{CellMesh::FaceIndexs::Bottom, IntVector(0, 0, -1)},
			{CellMesh::FaceIndexs::Top, IntVector(0, 0, 1)},
		};
		return to_vector[CellMesh::FaceIndexs(face_index)];
	}
	/**
	 * 6面インデックスを反転
	 * @param face_index 6面インデックス
	 * @return 反転した6面インデックス
	 */
	public: static int invert_face_index(int face_index) {
		std::map<int, int> to_faces = {
			{(int)(CellMesh::FaceIndexs::Left), (int)(CellMesh::FaceIndexs::Right)},
			{(int)(CellMesh::FaceIndexs::Right), (int)(CellMesh::FaceIndexs::Left)},
			{(int)(CellMesh::FaceIndexs::Back), (int)(CellMesh::FaceIndexs::Front)},
			{(int)(CellMesh::FaceIndexs::Front), (int)(CellMesh::FaceIndexs::Back)},
			{(int)(CellMesh::FaceIndexs::Bottom), (int)(CellMesh::FaceIndexs::Top)},
			{(int)(CellMesh::FaceIndexs::Top), (int)(CellMesh::FaceIndexs::Bottom)},
		};
		return to_faces[face_index];
	}
	/**
	 * 面のバウンドボックスから6面インデックスに変換
	 * @param face_box 面のバウンドボックス
	 * @param unit 単位
	 * @return 6面インデックス
	 */
	public: static int face_box_to_face_index(Box3d face_box, int unit) {
		Vector cell_center_location = face_box.min + unit / 2;
		IntVector cell = CellMesh::to_cell(cell_center_location, unit);
		Vector cell_base_location = CellMesh::from_cell(cell, unit);
		Vector face_size = face_box.max - face_box.min;
		Vector face_offset_location = face_box.min - cell_base_location;
		Vector face_center_location = (face_offset_location + face_size) * 3 / 2;
		IntVector face_offset = CellMesh::to_cell(face_center_location, unit);
		int face_index = CellMesh::offset_cell_to_face_index(face_offset);
		printf("cell: (%d, %d, %d), face_offset: (%d, %d, %d), face_size: (%.2f, %.2f, %.2f), cell_base_location: (%.2f, %.2f, %.2f), cell_center_location: (%.2f, %.2f, %.2f), face_offset_location: (%.2f, %.2f, %.2f), face_center_location: (%.2f, %.2f, %.2f), result: %d", cell.x, cell.y, cell.z, face_offset.x, face_offset.y, face_offset.z, face_size.x, face_size.y, face_size.z, cell_base_location.x, cell_base_location.y, cell_base_location.z, cell_center_location.x, cell_center_location.y, cell_center_location.z, face_offset_location.x, face_offset_location.y, face_offset_location.z, face_center_location.x, face_center_location.y, face_center_location.z, face_index);
		return face_index;
	}
	/**
	 * セルのバウンドボックスを取得
	 * @param cell セル座標
	 * @param unit 単位
	 * @return バウンドボックス
	 */
	public: static Box3d to_cell_box(IntVector cell, int unit) {
		Vector min_location = CellMesh::from_cell(cell, unit);
		Vector max_location = CellMesh::from_cell(cell + IntVector(1, 1, 1), unit);
		return Box3d(min_location, max_location);
	}
	/**
	 * セルの8頂点を囲うバウンドボックスを取得
	 * @param coll_box セルのバウンドボックス
	 * @param unit 単位
	 * @return 頂点毎のバウンドボックスリスト
	 */
	public: static std::vector<Box3d> to_vertex_boxs(Box3d cell_box, int unit) {
		float offset = unit / 10.0;
		Vector min = cell_box.min;
		Vector max = cell_box.max;
		std::vector<Vector> positions = {
			{Vector(min.x, min.y, min.z)},
			{Vector(max.x, min.y, min.z)},
			{Vector(max.x, max.y, min.z)},
			{Vector(min.x, max.y, min.z)},
			{Vector(min.x, min.y, max.z)},
			{Vector(max.x, min.y, max.z)},
			{Vector(max.x, max.y, max.z)},
			{Vector(min.x, max.y, max.z)},
		};
		return [&]() -> std::vector<Box3d> {
			std::vector<Box3d> __ret;
			for (auto& position : positions) {
				__ret.push_back(Box3d(position - offset, position + offset));
			}
			return __ret;
		}();
	}
	/**
	 * セルの6面を囲うバウンドボックスを取得

	囲うために実際のバウンドボックスより10%大きいサイズになる点に注意
	 * @param coll_box セルのバウンドボックス
	 * @param unit 単位
	 * @return 面毎のバウンドボックスリスト
	 */
	public: static std::vector<Box3d> to_polygon_boxs(Box3d cell_box, int unit) {
		float offset = unit / 10;
		Vector min = cell_box.min;
		Vector max = cell_box.max;
		return {
			{Box3d(Vector(min.x - offset, min.y - offset, min.z - offset), Vector(min.x + offset, max.y + offset, max.z + offset))},
			{Box3d(Vector(max.x - offset, min.y - offset, min.z - offset), Vector(max.x + offset, max.y + offset, max.z + offset))},
			{Box3d(Vector(min.x - offset, min.y - offset, min.z - offset), Vector(max.x + offset, min.y + offset, max.z + offset))},
			{Box3d(Vector(min.x - offset, max.y - offset, min.z - offset), Vector(max.x + offset, max.y + offset, max.z + offset))},
			{Box3d(Vector(min.x - offset, min.y - offset, min.z - offset), Vector(max.x + offset, max.y + offset, min.z + offset))},
			{Box3d(Vector(min.x - offset, min.y - offset, max.z - offset), Vector(max.x + offset, max.y + offset, max.z + offset))},
		};
	}
	/**
	 * セルの8頂点の頂点IDを取得する
	 * @param mesh ダイナミックメッシュ
	 * @param cell セル座標
	 * @param unit 単位
	 * @return 頂点IDリスト
	 */
	public: static std::vector<int> by_vertex_ids(Mesh* mesh, IntVector cell, int unit) {
		std::vector<int> outIds = {
			{-1},
			{-1},
			{-1},
			{-1},
			{-1},
			{-1},
			{-1},
			{-1},
		};
		auto closure = [&](const MeshRaw& origin) -> void {
			Box3d cellBox = CellMesh::to_cell_box(cell, unit);
			std::vector<Box3d> boxs = CellMesh::to_vertex_boxs(cellBox, unit);
			for (auto& [i, box] : [&]() -> std::map<int, Box3d> {
				std::map<int, Box3d> __ret;
				int __index = 0;
				for (auto& __entry : boxs) {
					__ret.emplace(__index++, __entry);
				}
				return __ret;
			}()) {
				for (auto& vi : origin.vertex_indices_itr()) {
					if (!origin.is_vertex(vi)) {
						continue;
					}
					Vector v = origin.get_vertex(vi);
					if (box.contains(v)) {
						outIds[i] = vi;
						break;
					}
				}
			}
		}
		mesh->process_mesh(closure);
		return outIds;
	}
};