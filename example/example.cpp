#pragma once
class IntVector {
	public: IntVector(int x, int y, int z) {
		self.x = x;
		self.y = y;
		self.z = z;
	}
};
class CellMesh {
	enum class FaceIndexs {
		Max = 6,
		Top = 5,
		Bottom = 4,
		Front = 3,
		Back = 2,
		Right = 1,
		Left = 0,
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