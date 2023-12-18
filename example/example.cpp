pragma()


class IntVector {


	public: IntVector( self, int x, int y, int z) {
		self.x = x;
		self.y = y;
		self.z = z;
	}
};
Left = 0;
Right = 1;
Back = 2;
Front = 3;
Bottom = 4;
Top = 5;
Max = 6;
enum class FaceIndexs {
	Left = 0,
	Right = 1,
	Back = 2,
	Front = 3,
	Bottom = 4,
	Top = 5,
	Max = 6,
};
"""面インデックスからベクトルに変換

		Args:
			faceIndex (int): 6面インデックス
		Returns:
			IntVector: ベクトル
		"""
{

	,

};
"""面インデックスからベクトルに変換

		Args:
			faceIndex (int): 6面インデックス
		Returns:
			IntVector: ベクトル
		""""""面インデックスからベクトルに変換

		Args:
			faceIndex (int): 6面インデックス
		Returns:
			IntVector: ベクトル
		"""
map
dict
CellMesh.FaceIndexs
IntVector
CellMesh.FaceIndexs.Left
IntVector
-
1(, , )
CellMesh.FaceIndexs.Right
IntVector(, , )
CellMesh.FaceIndexs.Back
IntVector
0
-(, , )
CellMesh.FaceIndexs.Front
IntVector(, , )
CellMesh.FaceIndexs.Bottom
IntVector
0
0(, , )


class CellMesh {

	IntVector(, , )CellMesh.FaceIndexs.Top = {
		{CellMesh.FaceIndexs.Left, IntVector-1-1-1-10000},
		{CellMesh.FaceIndexs.Right, IntVector110000},
		{CellMesh.FaceIndexs.Back, IntVector00-1-1-1-100},
		{CellMesh.FaceIndexs.Front, IntVector001100},
		{CellMesh.FaceIndexs.Bottom, IntVector0000-1-1-1-1},
		{CellMesh.FaceIndexs.Top, IntVector000011},
	};;

	public: static faceIndexToVector( cls, int faceIndex) {
		map
		CellMesh.FaceIndexs
		return CellMesh.FaceIndexs();
	}
};