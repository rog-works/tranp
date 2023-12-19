#pragma once
class Vector {
	public: float self.x;
	public: float self.y;
	public: float self.z;

	public: Vector(float x, float y, float z) {
		float self.x = x;
		float self.y = y;
		float self.z = z;
	}
};
class IntVector {
	public: int self.x;
	public: int self.y;
	public: int self.z;

	public: IntVector(int x, int y, int z) {
		int self.x = x;
		int self.y = y;
		int self.z = z;
	}
};
class CellMesh {
	enum class FaceIndexs {
		Left = 0,
		Right = 1,
		Back = 2,
		Front = 3,
		Bottom = 4,
		Top = 5,
		Max = 6,
	};
	public: static Vector fromCell(IntVector cell, int unit = 100) {
		cell.x = cell.x * unit;
		cell.y = cell.y * unit;
		cell.z = cell.z * unit;
		fx = float(cell.x);
		fy = float(cell.y);
		fz = float(cell.z);
		return Vector(fz, fy, fx);
	}
	public: static IntVector faceIndexToVector(int faceIndex) {
		std::map<CellMesh.FaceIndexs, IntVector> map = {
			{CellMesh.FaceIndexs.Left, IntVector(0, 0, -1)},
			{CellMesh.FaceIndexs.Right, IntVector(0, 0, 1)},
			{CellMesh.FaceIndexs.Back, IntVector(0, -1, 0)},
			{CellMesh.FaceIndexs.Front, IntVector(0, 1, 0)},
			{CellMesh.FaceIndexs.Bottom, IntVector(-1, 0, 0)},
			{CellMesh.FaceIndexs.Top, IntVector(1, 0, 0)},
		};
		return map[CellMesh.FaceIndexs(faceIndex)];
	}
};