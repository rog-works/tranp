// #include "typing.h"
// #include "py2cpp/compatible/cpp/preprocess.h"
// #include "py2cpp/compatible/cpp/enum.h"
// #include "py2cpp/compatible/cpp/object.h"
#pragma once
using Enum = CEnum;
#include "example/FW/compatible.h"
/**
 * 3Dレンジオブジェクト
 */
class Box3d {
	public: Vector min;
	public: Vector max;
	/**
	 * インスタンスを生成
	 * @param min 開始座標
	 * @param max 終了座標
	 */
	public: Box3d(Vector min, Vector max) : min(min), max(max) {
	}
	/** contains */
	public: bool contains(Vector location) {
		throw new Exception("Not implemented");
	}
};
/** CellMesh */
class CellMesh {
	/** VertexIndexs */
	enum class VertexIndexs {
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
	/** FaceIndexs */
	enum class FaceIndexs {
		Left = 0,
		Right = 1,
		Back = 2,
		Front = 3,
		Bottom = 4,
		Top = 5,
		Max = 6,
	};
	/** from_cell */
	public: static std::shared_ptr<Vector> from_cell(IntVector cell, int unit = 100) {
		cell.x = cell.x * unit;
		cell.y = cell.y * unit;
		cell.z = cell.z * unit;
		float fx = float(cell.x);
		float fy = float(cell.y);
		float fz = float(cell.z);
		print("%f, %f, %f", fx, fy, fz);
		return new Vector(fx, fy, fz);
	}
	/** face_index_to_vector */
	public: static IntVector face_index_to_vector(int faceIndex) {
		std::map<CellMesh.FaceIndexs, IntVector> map = {
			{CellMesh::FaceIndexs::Left, IntVector(-1, 0, 0)},
			{CellMesh::FaceIndexs::Right, IntVector(1, 0, 0)},
			{CellMesh::FaceIndexs::Back, IntVector(0, -1, 0)},
			{CellMesh::FaceIndexs::Front, IntVector(0, 1, 0)},
			{CellMesh::FaceIndexs::Bottom, IntVector(0, 0, -1)},
			{CellMesh::FaceIndexs::Top, IntVector(0, 0, 1)},
		};
		return map[CellMesh::FaceIndexs(faceIndex)];
	}
	/** to_cell_box */
	public: static const std::shared_ptr<Box3d> to_cell_box(IntVector cell, int unit) {
		std::shared_ptr<Vector> minLocation = CellMesh::from_cell(cell, unit);
		std::shared_ptr<Vector> maxLocation = CellMesh::from_cell(cell + IntVector(1, 1, 1), unit);
		return Box3d(minLocation, maxLocation);
	}
	/** to_vertex_boxs */
	public: static std::vector<std::shared_ptr<Box3d>> to_vertex_boxs(Box3d* cellBox, int unit) {
		float offset = unit / 10.0;
		Vector min = cellBox->min;
		Vector max = cellBox->max;
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
		std::vector<std::shared_ptr<Box3d>> out = {
		};
		Vector* p = positions[0];
		for (auto position : positions) {
			out.push_back(new Box3d(position - offset, position + offset));
		}
		return out;
	}
	/** by_vertex_ids */
	public: static std::vector<int> by_vertex_ids(Mesh mesh, IntVector cell, int unit) {
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
		auto closure = [&](MeshRaw origin) -> void {
			const std::shared_ptr<Box3d> cellBox = CellMesh::to_cell_box(cell, unit);
			std::vector<Box3d<CSP>> boxs = CellMesh::to_vertex_boxs(cellBox, unit);
			for (auto i : range(int(CellMesh::VertexIndexs::Max))) {
				std::shared_ptr<Box3d> box = boxs[i];
				for (auto vi : origin.vertex_indices_itr()) {
					if (!origin.is_vertex(vi)) {
						continue;
					}
					Vector v = origin.get_vertex(vi);
					if (box->contains(v)) {
						outIds[i] = vi;
						break;
					}
				}
			}
		}
		mesh.process_mesh(closure);
		return outIds;
	}
};