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
			{(int)(CellMesh::NeedCellIndexs::Bottom0), { {(int)(CellMesh::FaceIndexs::Bottom)}, {(int)(CellMesh::FaceIndexs::Back)}, }},
			{(int)(CellMesh::NeedCellIndexs::Bottom1), { {(int)(CellMesh::FaceIndexs::Bottom)}, {(int)(CellMesh::FaceIndexs::Left)}, }},
			{(int)(CellMesh::NeedCellIndexs::Bottom2), { {(int)(CellMesh::FaceIndexs::Bottom)}, {(int)(CellMesh::FaceIndexs::Right)}, }},
			{(int)(CellMesh::NeedCellIndexs::Bottom3), { {(int)(CellMesh::FaceIndexs::Bottom)}, {(int)(CellMesh::FaceIndexs::Front)}, }},
			{(int)(CellMesh::NeedCellIndexs::Middle0), { {(int)(CellMesh::FaceIndexs::Back)}, {(int)(CellMesh::FaceIndexs::Left)}, }},
			{(int)(CellMesh::NeedCellIndexs::Middle1), { {(int)(CellMesh::FaceIndexs::Back)}, {(int)(CellMesh::FaceIndexs::Right)}, }},
			{(int)(CellMesh::NeedCellIndexs::Middle2), { {(int)(CellMesh::FaceIndexs::Front)}, {(int)(CellMesh::FaceIndexs::Left)}, }},
			{(int)(CellMesh::NeedCellIndexs::Middle3), { {(int)(CellMesh::FaceIndexs::Front)}, {(int)(CellMesh::FaceIndexs::Right)}, }},
			{(int)(CellMesh::NeedCellIndexs::Top0), { {(int)(CellMesh::FaceIndexs::Top)}, {(int)(CellMesh::FaceIndexs::Back)}, }},
			{(int)(CellMesh::NeedCellIndexs::Top1), { {(int)(CellMesh::FaceIndexs::Top)}, {(int)(CellMesh::FaceIndexs::Left)}, }},
			{(int)(CellMesh::NeedCellIndexs::Top2), { {(int)(CellMesh::FaceIndexs::Top)}, {(int)(CellMesh::FaceIndexs::Right)}, }},
			{(int)(CellMesh::NeedCellIndexs::Top3), { {(int)(CellMesh::FaceIndexs::Top)}, {(int)(CellMesh::FaceIndexs::Front)}, }},
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
			{(int)(CellMesh::FaceIndexs::Left), { {(int)(CellMesh::FaceIndexs::Back)}, {(int)(CellMesh::FaceIndexs::Front)}, {(int)(CellMesh::FaceIndexs::Bottom)}, {(int)(CellMesh::FaceIndexs::Top)}, }},
			{(int)(CellMesh::FaceIndexs::Right), { {(int)(CellMesh::FaceIndexs::Back)}, {(int)(CellMesh::FaceIndexs::Front)}, {(int)(CellMesh::FaceIndexs::Bottom)}, {(int)(CellMesh::FaceIndexs::Top)}, }},
			{(int)(CellMesh::FaceIndexs::Back), { {(int)(CellMesh::FaceIndexs::Left)}, {(int)(CellMesh::FaceIndexs::Right)}, {(int)(CellMesh::FaceIndexs::Bottom)}, {(int)(CellMesh::FaceIndexs::Top)}, }},
			{(int)(CellMesh::FaceIndexs::Front), { {(int)(CellMesh::FaceIndexs::Left)}, {(int)(CellMesh::FaceIndexs::Right)}, {(int)(CellMesh::FaceIndexs::Bottom)}, {(int)(CellMesh::FaceIndexs::Top)}, }},
			{(int)(CellMesh::FaceIndexs::Bottom), { {(int)(CellMesh::FaceIndexs::Left)}, {(int)(CellMesh::FaceIndexs::Right)}, {(int)(CellMesh::FaceIndexs::Back)}, {(int)(CellMesh::FaceIndexs::Front)}, }},
			{(int)(CellMesh::FaceIndexs::Top), { {(int)(CellMesh::FaceIndexs::Left)}, {(int)(CellMesh::FaceIndexs::Right)}, {(int)(CellMesh::FaceIndexs::Back)}, {(int)(CellMesh::FaceIndexs::Front)}, }},
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
		return to_vector[(CellMesh::FaceIndexs)(face_index)];
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
	 * 囲うために実際のバウンドボックスより10%大きいサイズになる点に注意
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
	 * @param mesh メッシュ
	 * @param cell セル座標
	 * @param unit 単位
	 * @return 頂点IDリスト
	 */
	public: static std::vector<int> by_vertex_ids(Mesh* mesh, IntVector cell, int unit) {
		std::vector<int> out_ids = {
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
			Box3d cell_box = CellMesh::to_cell_box(cell, unit);
			std::vector<Box3d> boxs = CellMesh::to_vertex_boxs(cell_box, unit);
			for (auto i = 0; i < boxs.size(); i++) {
				Box3d& box = boxs[i];
				for (auto& vi : origin.vertex_indices_itr()) {
					if (!origin.is_vertex(vi)) {
						continue;
					}
					Vector v = origin.get_vertex(vi);
					if (box.contains(v)) {
						out_ids[i] = vi;
						break;
					}
				}
			}
		}
		mesh->process_mesh(closure);
		return out_ids;
	}
	/**
	 * 指定のセル座標から3x3x3の範囲に存在するセルの6面のポリゴンIDを取得する
	 * @param mesh メッシュ
	 * @param start 取得開始セル座標
	 * @param unit 単位
	 * @return ポリゴンIDリスト
	 */
	public: static std::map<IntVector, std::vector<IntVector2>> by_polygon_ids_impl(Mesh* mesh, IntVector start, int unit) {
		std::map<IntVector, std::map<int, IntVector2>> cell_on_faces = {};
		auto closure = [&](MeshRaw& origin) -> void {
			IntVector size = IntVector(3, 3, 3);
			Box3d box = Box3d(CellMesh::from_cell(start), CellMesh::from_cell(start + size));
			for (auto& ti : origin.triangle_indices_itr()) {
				if (!origin.is_triangle(ti)) {
					continue;
				}
				Box3d face_box = origin.get_tri_bounds(ti);
				if (!box.contains(face_box)) {
					continue;
				}
				Vector center_location = face_box.min + unit / 2;
				IntVector cell = CellMesh::to_cell(center_location, unit);
				int face_index = CellMesh::face_box_to_face_index(face_box, unit);
				if ((!cell_on_faces.contains(cell))) {
					cell_on_faces[cell] = {};
				}
				if ((!cell_on_faces[cell].contains(face_index))) {
					cell_on_faces[cell][face_index] = IntVector2(ti, -1);
				} else {
					cell_on_faces[cell][face_index].y = ti;
				}
				IntVector cell2 = cell + CellMesh::face_index_to_vector(face_index);
				int face_index2 = CellMesh::invert_face_index(face_index);
				if ((!cell_on_faces.contains(cell2))) {
					cell_on_faces[cell2] = {};
				}
				if ((!cell_on_faces[cell2].contains(face_index2))) {
					cell_on_faces[cell2][face_index2] = IntVector2(ti, -1);
				} else {
					cell_on_faces[cell2][face_index2].y = ti;
				}
				printf("Collect polygon. ti: %d, start: (%d, %d, %d), cell: (%d, %d, %d), faceIndex: %d, cell2: (%d, %d, %d), faceIndex2: %d, faceBox.min: (%f, %f, %f), faceBox.max: (%f, %f, %f), box.min: (%f, %f, %f), box.max: (%f, %f, %f)", ti, start.x, start.y, start.z, cell.x, cell.y, cell.z, face_index, cell2.x, cell2.y, cell2.z, face_index2, face_box.min.x, face_box.min.y, face_box.min.z, face_box.max.x, face_box.max.y, face_box.max.z, box.min.x, box.min.y, box.min.z, box.max.x, box.max.y, box.max.z);
			}
		}
		mesh->process_mesh(closure);
		for (auto& [cell, in_faces] : cell_on_faces) {
			for (auto& [face_index, face] : in_faces) {
				if (face.x != face.y && face.y == -1) {
					printf("Found invalid face. cell: (%d, %d, %d), face_index: (%d), pid: (%d, %d)", cell.x, cell.y, cell.z, face_index, face.x, face.y);
					face.x = -1;
					face.y = -1;
				}
			}
		}
		std::map<IntVector, std::vector<IntVector2>> out_ids = {};
		for (auto i = 0; i < (int)(CellMesh::OffsetIndexs::Max); i++) {
			IntVector offset = CellMesh::offset_index_to_cell(i);
			cell = start + offset;
			out_ids[cell] = [&]() -> std::vector<IntVector2> {
				std::vector<IntVector2> __ret;
				for (auto& _ : range((int)(CellMesh::FaceIndexs::Max))) {
					__ret.push_back(IntVector2(-1, -1));
				}
				return __ret;
			}();
			if ((!cell_on_faces.contains(cell))) {
				continue;
			}
			for (auto& [face_index, face] : cell_on_faces[cell]) {
				out_ids[cell][face_index] = face;
				printf("Found faces. cell: (%d, %d, %d), faceindex: %d, pid: (%d, %d)", cell.x, cell.y, cell.z, face_index, face.x, face.y);
			}
		}
		return out_ids;
	}
	/**
	 * セルの6面のポリゴンIDを取得する
	 * @param mesh メッシュ
	 * @param cell セル座標
	 * @param unit 単位
	 * @return ポリゴンIDリスト
	 */
	public: static std::vector<IntVector2> by_polygon_ids(Mesh* mesh, IntVector cell, int unit) {
		IntVector start = IntVector(cell.x - 1, cell.y - 1, cell.z - 1);
		std::map<IntVector, std::vector<IntVector2>> entries = CellMesh::by_polygon_ids_impl(mesh, start, unit);
		std::vector<IntVector> faces = {
			{start + IntVector(0, 1, 1)},
			{start + IntVector(2, 1, 1)},
			{start + IntVector(1, 0, 1)},
			{start + IntVector(1, 2, 1)},
			{start + IntVector(1, 1, 0)},
			{start + IntVector(1, 1, 2)},
		};
		std::vector<IntVector2> result = {
			{entries[faces[0]][(int)(CellMesh::FaceIndexs::Right)]},
			{entries[faces[1]][(int)(CellMesh::FaceIndexs::Left)]},
			{entries[faces[2]][(int)(CellMesh::FaceIndexs::Front)]},
			{entries[faces[3]][(int)(CellMesh::FaceIndexs::Back)]},
			{entries[faces[4]][(int)(CellMesh::FaceIndexs::Top)]},
			{entries[faces[5]][(int)(CellMesh::FaceIndexs::Bottom)]},
		};
		for (auto i = 0; i < (int)(CellMesh::FaceIndexs::Max); i++) {
			printf("Found faces by cell. i: %d, cell: (%d, %d, %d), start: (%d, %d, %d), face: (%d, %d, %d), result: (%d, %d)", i, cell.x, cell.y, cell.z, start.x, start.y, start.z, faces[i].x, faces[i].y, faces[i].z, result[i].x, result[i].y);
		}
		return result;
	}
	/**
	 * 指定座標へのセル追加に必要な周辺セルを取得
	 * @param mesh メッシュ
	 * @param cell セル座標
	 * @param unit 単位
	 * @return セル座標リスト
	 */
	public: static std::vector<IntVector> need_cells(Mesh* mesh, IntVector cell, int unit) {
		IntVector start = IntVector(cell.x - 1, cell.y - 1, cell.z - 1);
		std::map<IntVector, std::vector<IntVector2>> entries = CellMesh::by_polygon_ids_impl(mesh, start, unit);
		std::vector<IntVector2> entry = entries[cell];
		std::vector<IntVector> out_need_cells = {};
		for (auto i = 0; i < (int)(CellMesh::FaceIndexs::Max); i++) {
			if (entry[i].x != -1) {
				continue;
			}
			IntVector next = cell + CellMesh::face_index_to_vector(i);
			std::vector<IntVector2> next_entry = entries[next];
			for (auto& next_face_index : CellMesh::around_need_cell_face_indexs(i)) {
				IntVector2 next_face = next_entry[next_face_index];
				if (next_face.x == -1) {
					continue;
				}
				IntVector candidate = next + CellMesh::face_index_to_vector(next_face_index);
				if ((std::find(out_need_cells.begin(), out_need_cells.end(), candidate) != out_need_cells.end())) {
					continue;
				}
				out_need_cells.push_back(candidate);
				printf("Collect candidate. candidate: (%d, %d, %d)", candidate.x, candidate.y, candidate.z);
			}
		}
		for (auto i = 0; i < (int)(CellMesh::NeedCellIndexs::Max); i++) {
			for (auto& face_index : CellMesh::need_cell_face_indexs(i)) {
				IntVector2 face = entry[face_index];
				if (face.x == -1) {
					continue;
				}
				IntVector vector = CellMesh::face_index_to_vector(face_index);
				next = cell + vector;
				for (auto& next_face_index : CellMesh::around_need_cell_face_indexs(face_index)) {
					IntVector next_vector = CellMesh::face_index_to_vector(next_face_index);
					candidate = next + next_vector;
					out_need_cells.remove(candidate);
					printf("Remove candidates. faceIndex: %d, cell: (%d, %d, %d), vector: (%d, %d, %d), nextFaceIndex: %d, next: (%d, %d, %d), nextVector: (%d, %d, %d), candidate: (%d, %d, %d)", face_index, cell.x, cell.y, cell.z, vector.x, vector.y, vector.z, next_face_index, next.x, next.y, next.z, next_vector.x, next_vector.y, next_vector.z, candidate.x, candidate.y, candidate.z);
				}
			}
		}
		for (auto& need_cell : out_need_cells) {
			printf("Need cells. cell: (%d, %d, %d)", need_cell.x, need_cell.y, need_cell.z);
		}
		return out_need_cells;
	}
	/**
	 * 指定座標にセル追加が出来るか判定
	 * @param mesh メッシュ
	 * @param cell セル座標
	 * @param unit 単位
	 * @return True = OK, False = NG(周辺セルが不足)
	 */
	public: static bool addable(Mesh* mesh, IntVector cell, int unit) {
		return CellMesh::need_cells(mesh, cell, unit).size() == 0;
	}
	/**
	 * メッシュをクリーニングし、初期状態に戻す
	 * @param mesh メッシュ
	 */
	public: static void clear(Mesh* mesh) {
		auto closure = [&](MeshRaw& origin) -> void {
			origin.clear();
		}
		mesh->edit_mesh(closure);
	}
	/**
	 * 指定のセル座標にセルを追加
	 * # 追加条件:
	 * 周辺セルの不足によってトポロジーが崩れないことが条件
	 * 辺のみ接触する隣接セルが存在する場合が上記の条件に抵触する
	 * @param mesh メッシュ
	 * @param cell セル座標
	 * @param unit 単位 (default = 100cm)
	 */
	public: static void add_cell(Mesh* mesh, IntVector cell, int unit = 100) {
		if (!CellMesh::addable(mesh, cell, unit)) {
			printf("Cannot be added due to lack of surrounding cells. cell: (%d, %d, %d)", cell.x, cell.y, cell.z);
		}
		auto closure = [&](MeshRaw& origin) -> void {
			std::vector<int> v_ids = CellMesh::by_vertex_ids(mesh, cell, unit);
			std::vector<IntVector2> p_ids = CellMesh::by_polygon_ids(mesh, cell, unit);
			float f_unit = (float)(unit);
			std::vector<Vector> verts = {
				{Vector(0, 0, 0)},
				{Vector(f_unit, 0, 0)},
				{Vector(f_unit, f_unit, 0)},
				{Vector(0, f_unit, 0)},
				{Vector(0, 0, f_unit)},
				{Vector(f_unit, 0, f_unit)},
				{Vector(f_unit, f_unit, f_unit)},
				{Vector(0, f_unit, f_unit)},
			};
			Vector start = CellMesh::from_cell(cell);
			for (auto i = 0; i < 8; i++) {
				if (v_ids[i] == -1) {
					Vector pos = start + verts[i];
					v_ids[i] = origin.append_vertex(pos);
					printf("Add Vertex. i: %d, vid: %d, pos: (%f, %f, %f)", i, v_ids[i], pos.x, pos.y, pos.z);
				}
			}
			printf("Vertexs: %d, %d, %d, %d, %d, %d, %d, %d", v_ids[0], v_ids[1], v_ids[2], v_ids[3], v_ids[4], v_ids[5], v_ids[6], v_ids[7]);
			printf("Polygons: {%d, %d}, {%d, %d}, {%d, %d}, {%d, %d}, {%d, %d}, {%d, %d}", p_ids[0].x, p_ids[0].y, p_ids[1].x, p_ids[1].y, p_ids[2].x, p_ids[2].y, p_ids[3].x, p_ids[3].y, p_ids[4].x, p_ids[4].y, p_ids[5].x, p_ids[5].y);
			std::map<int, Vector2> uvs = {
				{0, Vector2(0.0, 0.0)},
				{1, Vector2(1.0, 0.0)},
				{2, Vector2(1.0, 1.0)},
				{3, Vector2(0.0, 1.0)},
			};
			if (!origin.has_attributes()) {
				origin.enable_attributes();
			}
			if (origin.attributes().num_uv_layers() == 0) {
				origin.attributes().set_num_uv_layers(1);
			}
			if (!origin.has_triangle_groups()) {
				origin.enable_triangle_groups(0);
			}
			std::map<CellMesh::FaceIndexs, std::vector<IntVector>> uv_map = {
				{CellMesh::FaceIndexs::Left, { {IntVector(3, 2, 1)}, {IntVector(3, 1, 0)}, }},
				{CellMesh::FaceIndexs::Right, { {IntVector(2, 1, 0)}, {IntVector(2, 0, 3)}, }},
				{CellMesh::FaceIndexs::Back, { {IntVector(2, 1, 0)}, {IntVector(2, 0, 3)}, }},
				{CellMesh::FaceIndexs::Front, { {IntVector(3, 2, 1)}, {IntVector(3, 1, 0)}, }},
				{CellMesh::FaceIndexs::Bottom, { {IntVector(0, 1, 2)}, {IntVector(0, 2, 3)}, }},
				{CellMesh::FaceIndexs::Top, { {IntVector(0, 3, 2)}, {IntVector(0, 2, 1)}, }},
			};
			std::map<CellMesh::FaceIndexs, std::vector<IntVector>> polygon_map = {
				{CellMesh::FaceIndexs::Left, { {IntVector(0, 3, 7)}, {IntVector(0, 7, 4)}, }},
				{CellMesh::FaceIndexs::Right, { {IntVector(1, 5, 6)}, {IntVector(1, 6, 2)}, }},
				{CellMesh::FaceIndexs::Back, { {IntVector(0, 4, 5)}, {IntVector(0, 5, 1)}, }},
				{CellMesh::FaceIndexs::Front, { {IntVector(3, 2, 6)}, {IntVector(3, 6, 7)}, }},
				{CellMesh::FaceIndexs::Bottom, { {IntVector(0, 1, 2)}, {IntVector(0, 2, 3)}, }},
				{CellMesh::FaceIndexs::Top, { {IntVector(4, 7, 6)}, {IntVector(4, 6, 5)}, }},
			};
			for (auto i = 0; i < 6; i++) {
				if (p_ids[i].x != -1) {
					origin.remove_triangle(p_ids[i].x);
					origin.remove_triangle(p_ids[i].y);
				}
			}
			UV uv_overlay = origin.attributes().primary_uv();
			for (auto i = 0; i < 6; i++) {
				if (p_ids[i].x != -1) {
					continue;
				}
				CellMesh::FaceIndexs key = (CellMesh::FaceIndexs)(i);
				std::vector<IntVector> polygon_entry = polygon_map[key];
				std::vector<IntVector> uv_entry = uv_map[key];
				int p_groupId = origin.max_group_id();
				for (auto j = 0; i < 2; j++) {
					IntVector& p = polygon_entry[j];
					IntVector polygon = IntVector(v_ids[p.x], v_ids[p.y], v_ids[p.z]);
					int polygon_id = origin.append_triangle(polygon);
					printf("Add Triangle. i: %d, j: %d, p: (%d, %d, %d), vid: (%d, %d, %d), result: %d, group: %d", i, j, p.x, p.y, p.z, v_ids[p.x], v_ids[p.y], v_ids[p.z], polygon_id, p_groupId);
					if (polygon_id < 0) {
						printf("Failed Add Triangle. i: %d, j: %d, p: (%d, %d, %d), vid: (%d, %d, %d), result: %d, group: %d", i, j, p.x, p.y, p.z, v_ids[p.x], v_ids[p.y], v_ids[p.z], polygon_id, p_groupId);
						continue;
					}
					origin.set_triangle_group(polygon_id, p_groupId);
					IntVector& uv_indexs = uv_entry[j];
					int uv_id1 = uv_overlay.append_element(uvs[uv_indexs.x]);
					int uv_id2 = uv_overlay.append_element(uvs[uv_indexs.y]);
					int uv_id3 = uv_overlay.append_element(uvs[uv_indexs.z]);
					uv_overlay.set_triangle(polygon_id, IntVector(uv_id1, uv_id2, uv_id3), true);
				}
			}
		}
		mesh->edit_mesh(closure);
	}
};