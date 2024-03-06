from abc import ABCMeta, abstractmethod
from typing import NamedTuple

from rogw.tranp.syntax.node.node import Node


class TranslatorOptions(NamedTuple):
	"""オプション

	Attributes:
		verbose (bool): ログ出力フラグ
	"""
	verbose: bool


class ITranslator(metaclass=ABCMeta):
	"""トランスレーターインターフェイス"""

	@property
	@abstractmethod
	def version(self) -> str:
		"""str: バージョン"""
		...

	@abstractmethod
	def translate(self, root: Node) -> str:
		"""起点のノードからASTを再帰的に解析してトランスパイル

		Args:
			root (Node): 起点のノード
		Returns:
			str: トランスパイル後のソースコード
		"""
		...
