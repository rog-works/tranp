from abc import ABCMeta, abstractmethod
from typing import Any, NamedTuple

from rogw.tranp.data.meta.types import TranspilerMeta
from rogw.tranp.syntax.node.node import Node


class TranspilerOptions(NamedTuple):
	"""トランスパイルオプション

	Attributes:
		verbose: ログ出力フラグ
		env: 環境変数
	"""
	verbose: bool
	env: dict[str, Any]


class ITranspiler(metaclass=ABCMeta):
	"""トランスパイラーインターフェイス"""

	@property
	@abstractmethod
	def meta(self) -> TranspilerMeta:
		"""Returns: トランスパイラーのメタ情報"""
		...

	@abstractmethod
	def transpile(self, root: Node) -> str:
		"""起点のノードから解析してトランスパイルしたソースコードを返却

		Args:
			root: 起点のノード
		Returns:
			トランスパイル後のソースコード
		"""
		...
