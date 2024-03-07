from abc import ABCMeta, abstractmethod
from typing import NamedTuple

from rogw.tranp.data.meta.types import TranspilerMeta
from rogw.tranp.syntax.node.node import Node


class TranspilerOptions(NamedTuple):
	"""トランスパイルオプション

	Attributes:
		verbose (bool): ログ出力フラグ
	"""

	verbose: bool


class ITranspiler(metaclass=ABCMeta):
	"""トランスパイラーインターフェイス"""

	@property
	@abstractmethod
	def meta(self) -> TranspilerMeta:
		"""TranspilerMeta: トランスパイラーのメタ情報"""
		...

	@abstractmethod
	def transpile(self, root: Node) -> str:
		"""起点のノードから解析してトランスパイルしたソースコードを返却

		Args:
			root (Node): 起点のノード
		Returns:
			str: トランスパイル後のソースコード
		"""
		...
