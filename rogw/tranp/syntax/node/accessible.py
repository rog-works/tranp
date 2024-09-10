from typing import ClassVar, Protocol


class ClassOperations(Protocol):
	"""クラスオペレーション定義のプロトコル

	Attributes:
		constructor: コンストラクターメソッドの名称
		copy_constructor: コピーコンストラクターメソッドの名称
		destructor: デストラクターメソッドの名称
		iterator: イテレーターメソッドの名称
		iterable: イテレータブルメソッドの名称
	"""

	constructor: ClassVar[str]
	copy_constructor: ClassVar[str]
	destructor: ClassVar[str]
	iterator: ClassVar[str]
	iterable: ClassVar[str]

	def operation_by(self, operator: str) -> str:
		"""各種演算に対応するメソッドの名称を取得

		Args:
			operator (str): 演算子
		Returns:
			str: メソッド名
		"""
		...

	def arthmetical(self, operator: str) -> bool:
		"""算術演算用の演算子か判定

		Args:
			operator (str): 演算子
		Returns:
			bool: True = 算術演算
		"""
		...
