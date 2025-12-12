from abc import ABCMeta, abstractmethod
from typing import Any, NamedTuple, Protocol

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
	def transpile(self, node: Node) -> str:
		"""起点のノードから解析してトランスパイルしたソースコードを返却

		Args:
			node: 起点のノード
		Returns:
			トランスパイル後のソースコード
		"""
		...


class Evaluator(Protocol):
	"""リテラル演算の結果を出力

	Args:
		node: 基点のノード
	Returns:
		演算結果
	Raises:
		Errors.OperationNotAllowed: 許可されない演算内容
	"""

	def exec(self, node: Node) -> int | float | str:
		"""@see Evaluator.Note"""
		...
