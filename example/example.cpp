// #include "py2cpp/compatible/cpp/directive.h"
// #include "py2cpp/compatible/cpp/enum.h"
#pragma once
#include "example/FW/compatible.h"
class Box3d {
	public: Vector self.min;
	public: Vector self.max;
	public: Box3d(Vector min, Vector max) : min(min), max(max) {
		Vector this.min = min;
		Vector this.max = max;
	}
	public: bool contains(Vector location) {
		throw new NotImplementedError();
	}
};
class CellMesh {
	enum class VertexIndexs {
		int BottomBackLeft = 0,
		int BottomBackRight = 1,
		int BottomFrontLeft = 2,
		int BottomFrontRight = 3,
		int TopBackLeft = 4,
		int TopBackRight = 5,
		int TopFrontLeft = 6,
		int TopFrontRight = 7,
		int Max = 8,
	};
	enum class FaceIndexs {
		int Left = 0,
		int Right = 1,
		int Back = 2,
		int Front = 3,
		int Bottom = 4,
		int Top = 5,
		int Max = 6,
	};
	classmethod()
	public: static Vector from_cell(IntVector cell, int unit = 100) {
		cell.x = cell.x * unit;
		cell.y = cell.y * unit;
		cell.z = cell.z * unit;
		float fx = float(cell.x);
		float fy = float(cell.y);
		float fz = float(cell.z);
		return Vector(fx, fy, fz);
	}
	classmethod()
	public: static IntVector face_index_to_vector(int faceIndex) {
		std::map<CellMesh.FaceIndexs, IntVector> map = {
			{CellMesh.FaceIndexs.Left, IntVector(-1, 0, 0)},
			{CellMesh.FaceIndexs.Right, IntVector(1, 0, 0)},
			{CellMesh.FaceIndexs.Back, IntVector(0, -1, 0)},
			{CellMesh.FaceIndexs.Front, IntVector(0, 1, 0)},
			{CellMesh.FaceIndexs.Bottom, IntVector(0, 0, -1)},
			{CellMesh.FaceIndexs.Top, IntVector(0, 0, 1)},
		};
		return map[CellMesh.FaceIndexs(faceIndex)];
	}
	classmethod()
	public: static Box3d to_cell_box(IntVector cell, int unit) {
		Vector minLocation = CellMesh.from_cell(cell, unit);
		Vector maxLocation = CellMesh.from_cell(cell + IntVector(1, 1, 1), unit);
		return Box3d(minLocation, maxLocation);
	}
	classmethod()
	public: static std::vector<Box3d> to_vertex_boxs(Box3d cellBox, int unit) {
		int offset = unit / 10;
		Vector min = cellBox.min;
		Vector max = cellBox.max;
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
		std::vector<Box3d> out = {
		};
		for (auto position : positions) {
			out.append(Box3d(position - offset, position + offset))
		}
		return out;
	}
	classmethod()
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
			Box3d cellBox = CellMesh.to_cell_box(cell, unit);
			std::vector<Box3d> boxs = CellMesh.to_vertex_boxs(cellBox, unit);
			for (auto i : range(int(CellMesh.VertexIndexs.Max))) {
				Box3d box = boxs[i];
				for (auto vi : origin.vertex_indices_itr()) {
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
		mesh.process_mesh(closure)
		return outIds;
	}
};