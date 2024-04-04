from typing import ClassVar, Protocol


class ClassOperations(Protocol):
	"""クラスオペレーション定義のプロトコル

	Attributes:
		constructor: コンストラクターメソッドの名称
		iterator: イテレーターメソッドの名称
		iterable: イテレータブルメソッドの名称
	"""

	constructor: ClassVar[str]
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
