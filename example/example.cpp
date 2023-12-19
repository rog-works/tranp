#pragma once
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