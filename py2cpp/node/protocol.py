from typing import Protocol

from py2cpp.node.node import Node


class Symbolization(Protocol):
	"""シンボルを保有するノードの共通インターフェイス。主に循環参照回避に用いる"""

	@property
	def symbol(self) -> Node:
		"""Node: シンボルノード"""
		...
