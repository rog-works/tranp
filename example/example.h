// @tranp.meta: {"version":"1.0.0","module":{"hash":"1ba02029e9df5f4ea099dd98edbe8b1a","path":"example.example"},"transpiler":{"version":"1.0.0","module":"rogw.tranp.implements.cpp.transpiler.py2cpp.Py2Cpp"}}
#pragma once
// #include "rogw/tranp/compatible/cpp/object.h"
// #include "rogw/tranp/compatible/cpp/preprocess.h"
// #include "rogw/tranp/compatible/cpp/enum.h"
#pragma once
#include "FW/compatible.h"
#include "FW/core.h"
/**
 * セル(メッシュ)関連のライブラリー
 */
class FL_CellMesh {
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
	public:
	/**
	 * セル座標に変換
	 * @param location 座標
	 * @param unit 単位(default = 100cm)
	 * @return セル座標
	 * @note 単位の倍数に近い座標で変換を行うのは不正確になり得るため注意が必要
	 */
	static IntVector to_cell(Vector location, int unit = 100) {
		IntVector cell = IntVector(static_cast<int>(location.x), static_cast<int>(location.y), static_cast<int>(location.z));
		return IntVector(static_cast<int>(cell.x / unit) + (location.x < 0 ? -1 : 0), static_cast<int>(cell.y / unit) + (location.y < 0 ? -1 : 0), static_cast<int>(cell.z / unit) + (location.z < 0 ? -1 : 0));
	}
	public:
	/**
	 * セル座標を座標に変換
	 * @param cell セル座標
	 * @param unit 単位(default = 100cm)
	 * @return 座標
	 */
	static Vector from_cell(IntVector cell, int unit = 100) {
		return Vector(static_cast<float>(cell.x * unit), static_cast<float>(cell.y * unit), static_cast<float>(cell.z * unit));
	}
	public:
	/**
	 * 座標からセルの中心座標に変換
	 * @param location 座標
	 * @param unit 単位(default = 100cm)
	 * @return セルの中心座標
	 * @note 単位の倍数に近い座標で変換を行うのは不正確になり得るため注意が必要
	 */
	static Vector to_center(Vector location, int unit = 100) {
		Vector based = FL_CellMesh::from_cell(FL_CellMesh::to_cell(location, unit), unit);
		return based + static_cast<int>(unit / 2);
	}
	public:
	/**
	 * オフセットセル座標(3x3x3)をオフセットインデックスに変換
	 * @param offset_cell オフセットセル座標(3x3x3)
	 * @return オフセットインデックス(3x3x3)
	 */
	static int offset_cell_to_index(IntVector offset_cell) {
		return offset_cell.z * 9 + offset_cell.y * 3 + offset_cell.x;
	}
	public:
	/**
	 * オフセットインデックス(3x3x3)からオフセットセル座標に変換
	 * @param offset_index オフセットインデックス(3x3x3)
	 * @return オフセットセル座標(3x3x3)
	 */
	static IntVector offset_index_to_cell(int offset_index) {
		int x = static_cast<int>(offset_index % 3);
		int y = static_cast<int>(offset_index % 9 / 3);
		int z = static_cast<int>(offset_index / 9);
		return IntVector(x, y, z);
	}
	public:
	/**
	 * 必須セルに必要な6面インデックスを取得
	 * @param need_cell_index 必須セルインデックス
	 * @return 6面インデックスリスト
	 * @note needCells専用
	 */
	static std::vector<int> need_cell_face_indexs(int need_cell_index) {
		std::map<int, std::vector<int>> to_faces = {
			{static_cast<int>(FL_CellMesh::NeedCellIndexs::Bottom0), { {static_cast<int>(FL_CellMesh::FaceIndexs::Bottom)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Back)}, }},
			{static_cast<int>(FL_CellMesh::NeedCellIndexs::Bottom1), { {static_cast<int>(FL_CellMesh::FaceIndexs::Bottom)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Left)}, }},
			{static_cast<int>(FL_CellMesh::NeedCellIndexs::Bottom2), { {static_cast<int>(FL_CellMesh::FaceIndexs::Bottom)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Right)}, }},
			{static_cast<int>(FL_CellMesh::NeedCellIndexs::Bottom3), { {static_cast<int>(FL_CellMesh::FaceIndexs::Bottom)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Front)}, }},
			{static_cast<int>(FL_CellMesh::NeedCellIndexs::Middle0), { {static_cast<int>(FL_CellMesh::FaceIndexs::Back)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Left)}, }},
			{static_cast<int>(FL_CellMesh::NeedCellIndexs::Middle1), { {static_cast<int>(FL_CellMesh::FaceIndexs::Back)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Right)}, }},
			{static_cast<int>(FL_CellMesh::NeedCellIndexs::Middle2), { {static_cast<int>(FL_CellMesh::FaceIndexs::Front)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Left)}, }},
			{static_cast<int>(FL_CellMesh::NeedCellIndexs::Middle3), { {static_cast<int>(FL_CellMesh::FaceIndexs::Front)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Right)}, }},
			{static_cast<int>(FL_CellMesh::NeedCellIndexs::Top0), { {static_cast<int>(FL_CellMesh::FaceIndexs::Top)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Back)}, }},
			{static_cast<int>(FL_CellMesh::NeedCellIndexs::Top1), { {static_cast<int>(FL_CellMesh::FaceIndexs::Top)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Left)}, }},
			{static_cast<int>(FL_CellMesh::NeedCellIndexs::Top2), { {static_cast<int>(FL_CellMesh::FaceIndexs::Top)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Right)}, }},
			{static_cast<int>(FL_CellMesh::NeedCellIndexs::Top3), { {static_cast<int>(FL_CellMesh::FaceIndexs::Top)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Front)}, }},
		};
		return to_faces[need_cell_index];
	}
	public:
	/**
	 * 6面方向の先のセルの周辺に存在する必須セルへの方向を示す6面インデックスを取得
	 * @param face_index 6面インデックス
	 * @return 6面インデックスリスト
	 * @note needCells専用
	 */
	static std::vector<int> around_need_cell_face_indexs(int face_index) {
		std::map<int, std::vector<int>> to_faces = {
			{static_cast<int>(FL_CellMesh::FaceIndexs::Left), { {static_cast<int>(FL_CellMesh::FaceIndexs::Back)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Front)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Bottom)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Top)}, }},
			{static_cast<int>(FL_CellMesh::FaceIndexs::Right), { {static_cast<int>(FL_CellMesh::FaceIndexs::Back)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Front)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Bottom)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Top)}, }},
			{static_cast<int>(FL_CellMesh::FaceIndexs::Back), { {static_cast<int>(FL_CellMesh::FaceIndexs::Left)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Right)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Bottom)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Top)}, }},
			{static_cast<int>(FL_CellMesh::FaceIndexs::Front), { {static_cast<int>(FL_CellMesh::FaceIndexs::Left)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Right)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Bottom)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Top)}, }},
			{static_cast<int>(FL_CellMesh::FaceIndexs::Bottom), { {static_cast<int>(FL_CellMesh::FaceIndexs::Left)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Right)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Back)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Front)}, }},
			{static_cast<int>(FL_CellMesh::FaceIndexs::Top), { {static_cast<int>(FL_CellMesh::FaceIndexs::Left)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Right)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Back)}, {static_cast<int>(FL_CellMesh::FaceIndexs::Front)}, }},
		};
		return to_faces[face_index];
	}
	public:
	/**
	 * オフセットセル座標(3x3x3)を6面インデックスに変換
	 * @param offset_cell オフセットセル座標(3x3x3)
	 * @return 6面インデックス
	 */
	static int offset_cell_to_face_index(IntVector offset_cell) {
		int offset_index = FL_CellMesh::offset_cell_to_index(offset_cell);
		std::map<int, int> to_faces = {
			{static_cast<int>(FL_CellMesh::OffsetIndexs::Left), static_cast<int>(FL_CellMesh::FaceIndexs::Left)},
			{static_cast<int>(FL_CellMesh::OffsetIndexs::Right), static_cast<int>(FL_CellMesh::FaceIndexs::Right)},
			{static_cast<int>(FL_CellMesh::OffsetIndexs::Back), static_cast<int>(FL_CellMesh::FaceIndexs::Back)},
			{static_cast<int>(FL_CellMesh::OffsetIndexs::Front), static_cast<int>(FL_CellMesh::FaceIndexs::Front)},
			{static_cast<int>(FL_CellMesh::OffsetIndexs::Bottom), static_cast<int>(FL_CellMesh::FaceIndexs::Bottom)},
			{static_cast<int>(FL_CellMesh::OffsetIndexs::Top), static_cast<int>(FL_CellMesh::FaceIndexs::Top)},
		};
		if ((!to_faces.contains(offset_index))) {
			log_error("Fatal Error! offset_index: %d", offset_index);
			return 0;
		}
		return to_faces[offset_index];
	}
	public:
	/**
	 * 6面インデックスからベクトルに変換
	 * @param face_index 6面インデックス
	 * @return ベクトル
	 */
	static IntVector face_index_to_vector(int face_index) {
		std::map<FL_CellMesh::FaceIndexs, IntVector> to_vector = {
			{FL_CellMesh::FaceIndexs::Left, IntVector(-1, 0, 0)},
			{FL_CellMesh::FaceIndexs::Right, IntVector(1, 0, 0)},
			{FL_CellMesh::FaceIndexs::Back, IntVector(0, -1, 0)},
			{FL_CellMesh::FaceIndexs::Front, IntVector(0, 1, 0)},
			{FL_CellMesh::FaceIndexs::Bottom, IntVector(0, 0, -1)},
			{FL_CellMesh::FaceIndexs::Top, IntVector(0, 0, 1)},
		};
		return to_vector[static_cast<FL_CellMesh::FaceIndexs>(face_index)];
	}
	public:
	/**
	 * 6面インデックスを反転
	 * @param face_index 6面インデックス
	 * @return 反転した6面インデックス
	 */
	static int invert_face_index(int face_index) {
		std::map<int, int> to_faces = {
			{static_cast<int>(FL_CellMesh::FaceIndexs::Left), static_cast<int>(FL_CellMesh::FaceIndexs::Right)},
			{static_cast<int>(FL_CellMesh::FaceIndexs::Right), static_cast<int>(FL_CellMesh::FaceIndexs::Left)},
			{static_cast<int>(FL_CellMesh::FaceIndexs::Back), static_cast<int>(FL_CellMesh::FaceIndexs::Front)},
			{static_cast<int>(FL_CellMesh::FaceIndexs::Front), static_cast<int>(FL_CellMesh::FaceIndexs::Back)},
			{static_cast<int>(FL_CellMesh::FaceIndexs::Bottom), static_cast<int>(FL_CellMesh::FaceIndexs::Top)},
			{static_cast<int>(FL_CellMesh::FaceIndexs::Top), static_cast<int>(FL_CellMesh::FaceIndexs::Bottom)},
		};
		return to_faces[face_index];
	}
	public:
	/**
	 * 面のバウンドボックスから6面インデックスに変換
	 * @param face_box 面のバウンドボックス
	 * @param unit 単位
	 * @return 6面インデックス
	 */
	static int face_box_to_face_index(Box3d face_box, int unit) {
		Vector cell_center_location = face_box.min + unit / 2;
		IntVector cell = FL_CellMesh::to_cell(cell_center_location, unit);
		Vector cell_base_location = FL_CellMesh::from_cell(cell, unit);
		Vector face_size = face_box.max - face_box.min;
		Vector face_offset_location = face_box.min - cell_base_location;
		Vector face_center_location = (face_offset_location + face_size) * 3 / 2;
		IntVector face_offset = FL_CellMesh::to_cell(face_center_location, unit);
		int face_index = FL_CellMesh::offset_cell_to_face_index(face_offset);
		log_info("cell: (%d, %d, %d), face_offset: (%d, %d, %d), face_size: (%.2f, %.2f, %.2f), cell_base_location: (%.2f, %.2f, %.2f), cell_center_location: (%.2f, %.2f, %.2f), face_offset_location: (%.2f, %.2f, %.2f), face_center_location: (%.2f, %.2f, %.2f), result: %d", cell.x, cell.y, cell.z, face_offset.x, face_offset.y, face_offset.z, face_size.x, face_size.y, face_size.z, cell_base_location.x, cell_base_location.y, cell_base_location.z, cell_center_location.x, cell_center_location.y, cell_center_location.z, face_offset_location.x, face_offset_location.y, face_offset_location.z, face_center_location.x, face_center_location.y, face_center_location.z, face_index);
		return face_index;
	}
	public:
	/**
	 * セルのバウンドボックスを取得
	 * @param cell セル座標
	 * @param unit 単位
	 * @return バウンドボックス
	 */
	static Box3d to_cell_box(IntVector cell, int unit) {
		Vector min_location = FL_CellMesh::from_cell(cell, unit);
		Vector max_location = FL_CellMesh::from_cell(cell + IntVector(1, 1, 1), unit);
		return Box3d(min_location, max_location);
	}
	public:
	/**
	 * セルの8頂点を囲うバウンドボックスを取得
	 * @param coll_box セルのバウンドボックス
	 * @param unit 単位
	 * @return 頂点毎のバウンドボックスリスト
	 */
	static std::vector<Box3d> to_vertex_boxs(Box3d cell_box, int unit) {
		int offset = static_cast<int>(unit / 10);
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
	public:
	/**
	 * セルの6面を囲うバウンドボックスを取得
	 * 囲うために実際のバウンドボックスより10%大きいサイズになる点に注意
	 * @param coll_box セルのバウンドボックス
	 * @param unit 単位
	 * @return 面毎のバウンドボックスリスト
	 */
	static std::vector<Box3d> to_polygon_boxs(Box3d cell_box, int unit) {
		int offset = static_cast<int>(unit / 10);
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
	public:
	/**
	 * セルの8頂点の頂点IDを取得する
	 * @param mesh メッシュ
	 * @param cell セル座標
	 * @param unit 単位
	 * @return 頂点IDリスト
	 */
	static std::vector<int> by_vertex_ids(Mesh* mesh, IntVector cell, int unit) {
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
			Box3d cell_box = FL_CellMesh::to_cell_box(cell, unit);
			std::vector<Box3d> boxs = FL_CellMesh::to_vertex_boxs(cell_box, unit);
			for (auto i = 0; i < boxs.size(); i++) {
				Box3d& box = boxs[i];
				for (const auto& vi : origin.vertex_indices_itr()) {
					// 実体がない(参照カウント0)インデックスを除外
					if (!origin.is_vertex(vi)) {
						continue;
					}
					Vector v = origin.get_vertex(vi);
					// LogInfo('i: %d, box.min: (%f, %f, %f), box.max: (%f, %f, %f), v: (%f, %f, %f)', i, box.on.min.x, box.on.min.y, box.on.min.z, box.on.max.x, box.on.max.y, box.on.max.z, v.x, v.y, v.z)
					if (box.contains(v)) {
						out_ids[i] = vi;
						break;
					}
				}
			}
		};
		mesh->process_mesh(closure);
		return out_ids;
	}
	public:
	/**
	 * 指定のセル座標から3x3x3の範囲に存在するセルの6面のポリゴンIDを取得する
	 * @param mesh メッシュ
	 * @param start 取得開始セル座標
	 * @param unit 単位
	 * @return ポリゴンIDリスト
	 */
	static std::map<IntVector, std::vector<IntVector2>> by_polygon_ids_impl(Mesh* mesh, IntVector start, int unit) {
		std::map<IntVector, std::map<int, IntVector2>> cell_on_faces = {};
		auto closure = [&](const MeshRaw& origin) -> void {
			IntVector size = IntVector(3, 3, 3);
			Box3d box = Box3d(FL_CellMesh::from_cell(start), FL_CellMesh::from_cell(start + size));
			for (const auto& ti : origin.triangle_indices_itr()) {
				// 実体がない(参照カウント0)インデックスを除外
				if (!origin.is_triangle(ti)) {
					continue;
				}
				// box.Contains(faceBox)の場合、targetBoxがbox内に完全に内包される場合のみtrue
				Box3d face_box = origin.get_tri_bounds(ti);
				if (!box.contains(face_box)) {
					continue;
				}
				// XXX toCell(faceBox.Min, unit)とすると、面のバウンドボックスとセル座標がズレてしまうため、中心座標を元にセル座標を算出する
				Vector center_location = face_box.min + unit / 2;
				IntVector cell = FL_CellMesh::to_cell(center_location, unit);
				int face_index = FL_CellMesh::face_box_to_face_index(face_box, unit);
				if ((!cell_on_faces.contains(cell))) {
					cell_on_faces[cell] = {};
				}
				if ((!cell_on_faces[cell].contains(face_index))) {
					cell_on_faces[cell][face_index] = IntVector2(ti, -1);
				} else {
					cell_on_faces[cell][face_index].y = ti;
				}
				// 辺で接するもう一方のセルも追加
				IntVector cell2 = cell + FL_CellMesh::face_index_to_vector(face_index);
				int face_index2 = FL_CellMesh::invert_face_index(face_index);
				if ((!cell_on_faces.contains(cell2))) {
					cell_on_faces[cell2] = {};
				}
				if ((!cell_on_faces[cell2].contains(face_index2))) {
					cell_on_faces[cell2][face_index2] = IntVector2(ti, -1);
				} else {
					cell_on_faces[cell2][face_index2].y = ti;
				}
				log_info("Collect polygon. ti: %d, start: (%d, %d, %d), cell: (%d, %d, %d), faceIndex: %d, cell2: (%d, %d, %d), faceIndex2: %d, faceBox.min: (%f, %f, %f), faceBox.max: (%f, %f, %f), box.min: (%f, %f, %f), box.max: (%f, %f, %f)", ti, start.x, start.y, start.z, cell.x, cell.y, cell.z, face_index, cell2.x, cell2.y, cell2.z, face_index2, face_box.min.x, face_box.min.y, face_box.min.z, face_box.max.x, face_box.max.y, face_box.max.z, box.min.x, box.min.y, box.min.z, box.max.x, box.max.y, box.max.z);
			}
		};
		mesh->process_mesh(closure);
		// XXX 不要な判定だが、実装中は一旦ガード節を設ける
		for (auto& [cell, in_faces] : cell_on_faces) {
			for (auto& [face_index, face] : in_faces) {
				if (face.x != face.y && face.y == -1) {
					log_error("Found invalid face. cell: (%d, %d, %d), face_index: (%d), pid: (%d, %d)", cell.x, cell.y, cell.z, face_index, face.x, face.y);
					face.x = -1;
					face.y = -1;
				}
			}
		}
		std::map<IntVector, std::vector<IntVector2>> out_ids = {};
		for (auto i = 0; i < static_cast<int>(FL_CellMesh::OffsetIndexs::Max); i++) {
			IntVector offset = FL_CellMesh::offset_index_to_cell(i);
			IntVector cell = start + offset;
			out_ids[cell] = std::vector<IntVector2>(static_cast<int>(FL_CellMesh::FaceIndexs::Max), IntVector2(-1, -1));
			if ((!cell_on_faces.contains(cell))) {
				continue;
			}
			for (auto& [face_index, face] : cell_on_faces[cell]) {
				out_ids[cell][face_index] = face;
				log_info("Found faces. cell: (%d, %d, %d), faceindex: %d, pid: (%d, %d)", cell.x, cell.y, cell.z, face_index, face.x, face.y);
			}
		}
		return out_ids;
	}
	public:
	/**
	 * セルの6面のポリゴンIDを取得する
	 * @param mesh メッシュ
	 * @param cell セル座標
	 * @param unit 単位
	 * @return ポリゴンIDリスト
	 */
	static std::vector<IntVector2> by_polygon_ids(Mesh* mesh, IntVector cell, int unit) {
		IntVector start = IntVector(cell.x - 1, cell.y - 1, cell.z - 1);
		std::map<IntVector, std::vector<IntVector2>> entries = FL_CellMesh::by_polygon_ids_impl(mesh, start, unit);
		std::vector<IntVector> faces = {
			{start + IntVector(0, 1, 1)},
			{start + IntVector(2, 1, 1)},
			{start + IntVector(1, 0, 1)},
			{start + IntVector(1, 2, 1)},
			{start + IntVector(1, 1, 0)},
			{start + IntVector(1, 1, 2)},
		};
		std::vector<IntVector2> result = {
			{entries[faces[0]][static_cast<int>(FL_CellMesh::FaceIndexs::Right)]},
			{entries[faces[1]][static_cast<int>(FL_CellMesh::FaceIndexs::Left)]},
			{entries[faces[2]][static_cast<int>(FL_CellMesh::FaceIndexs::Front)]},
			{entries[faces[3]][static_cast<int>(FL_CellMesh::FaceIndexs::Back)]},
			{entries[faces[4]][static_cast<int>(FL_CellMesh::FaceIndexs::Top)]},
			{entries[faces[5]][static_cast<int>(FL_CellMesh::FaceIndexs::Bottom)]},
		};
		for (auto i = 0; i < static_cast<int>(FL_CellMesh::FaceIndexs::Max); i++) {
			log_info("Found faces by cell. i: %d, cell: (%d, %d, %d), start: (%d, %d, %d), face: (%d, %d, %d), result: (%d, %d)", i, cell.x, cell.y, cell.z, start.x, start.y, start.z, faces[i].x, faces[i].y, faces[i].z, result[i].x, result[i].y);
		}
		return result;
	}
	public:
	/**
	 * 指定座標へのセル追加に必要な周辺セルを取得
	 * @param mesh メッシュ
	 * @param cell セル座標
	 * @param unit 単位
	 * @return セル座標リスト
	 */
	static std::vector<IntVector> need_cells(Mesh* mesh, IntVector cell, int unit) {
		IntVector start = IntVector(cell.x - 1, cell.y - 1, cell.z - 1);
		std::map<IntVector, std::vector<IntVector2>> entries = FL_CellMesh::by_polygon_ids_impl(mesh, start, unit);
		std::vector<IntVector2> entry = entries[cell];
		// 6面方向の先にセルが存在しない場合、その周辺セルを候補として抽出
		std::vector<IntVector> out_need_cells = {};
		for (auto i = 0; i < static_cast<int>(FL_CellMesh::FaceIndexs::Max); i++) {
			if (entry[i].x != -1) {
				continue;
			}
			IntVector next = cell + FL_CellMesh::face_index_to_vector(i);
			std::vector<IntVector2> next_entry = entries[next];
			for (auto& next_face_index : FL_CellMesh::around_need_cell_face_indexs(i)) {
				IntVector2 next_face = next_entry[next_face_index];
				if (next_face.x == -1) {
					continue;
				}
				IntVector candidate = next + FL_CellMesh::face_index_to_vector(next_face_index);
				if ((std::find(out_need_cells.begin(), out_need_cells.end(), candidate) != out_need_cells.end())) {
					continue;
				}
				out_need_cells.push_back(candidate);
				log_info("Collect candidate. candidate: (%d, %d, %d)", candidate.x, candidate.y, candidate.z);
			}
		}
		// 必須セルに必要な面方向の先にセルが存在する場合、その周辺セルを候補から削除する
		for (auto i = 0; i < static_cast<int>(FL_CellMesh::NeedCellIndexs::Max); i++) {
			for (auto& face_index : FL_CellMesh::need_cell_face_indexs(i)) {
				IntVector2 face = entry[face_index];
				if (face.x == -1) {
					continue;
				}
				IntVector vector = FL_CellMesh::face_index_to_vector(face_index);
				IntVector next = cell + vector;
				for (auto& next_face_index : FL_CellMesh::around_need_cell_face_indexs(face_index)) {
					IntVector next_vector = FL_CellMesh::face_index_to_vector(next_face_index);
					IntVector candidate = next + next_vector;
					out_need_cells.erase(candidate);
					log_info("Remove candidates. faceIndex: %d, cell: (%d, %d, %d), vector: (%d, %d, %d), nextFaceIndex: %d, next: (%d, %d, %d), nextVector: (%d, %d, %d), candidate: (%d, %d, %d)", face_index, cell.x, cell.y, cell.z, vector.x, vector.y, vector.z, next_face_index, next.x, next.y, next.z, next_vector.x, next_vector.y, next_vector.z, candidate.x, candidate.y, candidate.z);
				}
			}
		}
		for (auto& need_cell : out_need_cells) {
			log_info("Need cells. cell: (%d, %d, %d)", need_cell.x, need_cell.y, need_cell.z);
		}
		return out_need_cells;
	}
	public:
	/**
	 * 指定座標にセル追加が出来るか判定
	 * @param mesh メッシュ
	 * @param cell セル座標
	 * @param unit 単位
	 * @return True = OK, False = NG(周辺セルが不足)
	 */
	static bool addable(Mesh* mesh, IntVector cell, int unit) {
		return FL_CellMesh::need_cells(mesh, cell, unit).size() == 0;
	}
	public:
	/**
	 * メッシュをクリーニングし、初期状態に戻す
	 * @param mesh メッシュ
	 */
	static void clear(Mesh* mesh) {
		auto closure = [&](MeshRaw& origin) -> void {
			origin.clear();
		};
		mesh->edit_mesh(closure);
	}
	public:
	/**
	 * 指定のセル座標にセルを追加
	 *
	 * # 追加条件:
	 * 周辺セルの不足によってトポロジーが崩れないことが条件
	 * 辺のみ接触する隣接セルが存在する場合が上記の条件に抵触する
	 * @param mesh メッシュ
	 * @param cell セル座標
	 * @param unit 単位 (default = 100cm)
	 */
	static void add_cell(Mesh* mesh, IntVector cell, int unit = 100) {
		if (!FL_CellMesh::addable(mesh, cell, unit)) {
			log_warning("Cannot be added due to lack of surrounding cells. cell: (%d, %d, %d)", cell.x, cell.y, cell.z);
		}
		auto closure = [&](MeshRaw& origin) -> void {
			std::vector<int> v_ids = FL_CellMesh::by_vertex_ids(mesh, cell, unit);
			std::vector<IntVector2> p_ids = FL_CellMesh::by_polygon_ids(mesh, cell, unit);
			// 頂点オーダー
			//    4-----5  Z
			//   /|    /|  |
			//  / 0---/-1  +---- X
			// 7-----6 /  /
			// |/    |/  /
			// 3-----2  Y
			float f_unit = static_cast<float>(unit);
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
			Vector start = FL_CellMesh::from_cell(cell);
			for (auto i = 0; i < static_cast<int>(FL_CellMesh::VertexIndexs::Max); i++) {
				if (v_ids[i] == -1) {
					Vector pos = start + verts[i];
					v_ids[i] = origin.append_vertex(pos);
					printf("Add Vertex. i: %d, vid: %d, pos: (%f, %f, %f)", i, v_ids[i], pos.x, pos.y, pos.z);
				}
				// else:
				// 	pos = start + verts[i];
				// 	print('Reuse Vertex. i: %d, vid: %d, pos: (%f, %f, %f)', i, vIds[i], pos.x, pos.y, pos.z)
			}
			log_info("Vertexs: %d, %d, %d, %d, %d, %d, %d, %d", v_ids[0], v_ids[1], v_ids[2], v_ids[3], v_ids[4], v_ids[5], v_ids[6], v_ids[7]);
			log_info("Polygons: {%d, %d}, {%d, %d}, {%d, %d}, {%d, %d}, {%d, %d}, {%d, %d}", p_ids[0].x, p_ids[0].y, p_ids[1].x, p_ids[1].y, p_ids[2].x, p_ids[2].y, p_ids[3].x, p_ids[3].y, p_ids[4].x, p_ids[4].y, p_ids[5].x, p_ids[5].y);
			std::map<int, Vector2> uvs = {
				{0, Vector2(0.0, 0.0)},
				{1, Vector2(1.0, 0.0)},
				{2, Vector2(1.0, 1.0)},
				{3, Vector2(0.0, 1.0)},
			};
			if (!origin.has_attributes()) {
				origin.enable_attributes();
			}
			if (origin.attributes()->num_uv_layers() == 0) {
				origin.attributes()->set_num_uv_layers(1);
			}
			if (!origin.has_triangle_groups()) {
				origin.enable_triangle_groups(0);
			}
			std::map<FL_CellMesh::FaceIndexs, std::vector<IntVector>> uv_map = {
				{FL_CellMesh::FaceIndexs::Left, { {IntVector(3, 2, 1)}, {IntVector(3, 1, 0)}, }},
				{FL_CellMesh::FaceIndexs::Right, { {IntVector(2, 1, 0)}, {IntVector(2, 0, 3)}, }},
				{FL_CellMesh::FaceIndexs::Back, { {IntVector(2, 1, 0)}, {IntVector(2, 0, 3)}, }},
				{FL_CellMesh::FaceIndexs::Front, { {IntVector(3, 2, 1)}, {IntVector(3, 1, 0)}, }},
				{FL_CellMesh::FaceIndexs::Bottom, { {IntVector(0, 1, 2)}, {IntVector(0, 2, 3)}, }},
				{FL_CellMesh::FaceIndexs::Top, { {IntVector(0, 3, 2)}, {IntVector(0, 2, 1)}, }},
			};
			std::map<FL_CellMesh::FaceIndexs, std::vector<IntVector>> polygon_map = {
				{FL_CellMesh::FaceIndexs::Left, { {IntVector(0, 3, 7)}, {IntVector(0, 7, 4)}, }},
				{FL_CellMesh::FaceIndexs::Right, { {IntVector(1, 5, 6)}, {IntVector(1, 6, 2)}, }},
				{FL_CellMesh::FaceIndexs::Back, { {IntVector(0, 4, 5)}, {IntVector(0, 5, 1)}, }},
				{FL_CellMesh::FaceIndexs::Front, { {IntVector(3, 2, 6)}, {IntVector(3, 6, 7)}, }},
				{FL_CellMesh::FaceIndexs::Bottom, { {IntVector(0, 1, 2)}, {IntVector(0, 2, 3)}, }},
				{FL_CellMesh::FaceIndexs::Top, { {IntVector(4, 7, 6)}, {IntVector(4, 6, 5)}, }},
			};
			// 隣接セルと重なった面を削除
			// ※トポロジーが崩れるため、面の追加より先に削除を行う
			// ※頂点やトライアングルグループは自動的に削除されるので何もしなくて良い
			for (auto i = 0; i < static_cast<int>(FL_CellMesh::FaceIndexs::Max); i++) {
				if (p_ids[i].x != -1) {
					origin.remove_triangle(p_ids[i].x);
					origin.remove_triangle(p_ids[i].y);
				}
			}
			// 隣接セルと重なっていない新規の面を追加
			UV* uv_overlay = origin.attributes()->primary_uv();
			for (auto i = 0; i < static_cast<int>(FL_CellMesh::FaceIndexs::Max); i++) {
				if (p_ids[i].x != -1) {
					continue;
				}
				FL_CellMesh::FaceIndexs key = static_cast<FL_CellMesh::FaceIndexs>(i);
				std::vector<IntVector>& polygon_entry = polygon_map[key];
				std::vector<IntVector>& uv_entry = uv_map[key];
				int p_group_id = origin.max_group_id();
				for (auto j = 0; j < 2; j++) {
					IntVector& p = polygon_entry[j];
					IntVector polygon = IntVector(v_ids[p.x], v_ids[p.y], v_ids[p.z]);
					int polygon_id = origin.append_triangle(polygon);
					log_info("Add Triangle. i: %d, j: %d, p: (%d, %d, %d), vid: (%d, %d, %d), result: %d, group: %d", i, j, p.x, p.y, p.z, v_ids[p.x], v_ids[p.y], v_ids[p.z], polygon_id, p_group_id);
					if (polygon_id < 0) {
						log_error("Failed Add Triangle. i: %d, j: %d, p: (%d, %d, %d), vid: (%d, %d, %d), result: %d, group: %d", i, j, p.x, p.y, p.z, v_ids[p.x], v_ids[p.y], v_ids[p.z], polygon_id, p_group_id);
						continue;
					}
					origin.set_triangle_group(polygon_id, p_group_id);
					IntVector& uv_indexs = uv_entry[j];
					int uv_id1 = uv_overlay->append_element(uvs[uv_indexs.x]);
					int uv_id2 = uv_overlay->append_element(uvs[uv_indexs.y]);
					int uv_id3 = uv_overlay->append_element(uvs[uv_indexs.z]);
					uv_overlay->set_triangle(polygon_id, IntVector(uv_id1, uv_id2, uv_id3), true);
				}
			}
		};
		mesh->edit_mesh(closure);
	}
};
