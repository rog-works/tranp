from abc import ABCMeta, abstractmethod
from typing import NamedTuple

from rogw.tranp.meta.types import TranslatorMeta
from rogw.tranp.module.module import Module


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
	def meta(self) -> TranslatorMeta:
		"""TranslatorMeta: トランスレーターのメタ情報"""
		...

	@abstractmethod
	def translate(self, module: Module) -> str:
		"""対象のモジュールを解析してトランスパイル

		Args:
			module (Module): モジュール
		Returns:
			str: トランスパイル後のソースコード
		"""
		...
