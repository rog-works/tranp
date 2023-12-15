from abc import abstractmethod


class NodeBase:
	"""ノードの抽象基底クラス。主にGeneric型の解決に利用"""

	@property
	@abstractmethod
	def fill_path(self) -> str:
		"""str: ルート要素からのフルパス"""
		...
