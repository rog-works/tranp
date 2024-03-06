from abc import ABCMeta, abstractmethod
from typing import NamedTuple, Protocol

from rogw.tranp.module.module import Module
from rogw.tranp.module.types import ModulePath


class TranslatorOptions(NamedTuple):
	"""オプション

	Attributes:
		verbose (bool): ログ出力フラグ
	"""
	verbose: bool


class MetaHeaderInjector(Protocol):
	"""メタヘッダー注入プロトコル

	Note:
		このプロトコルの出力がトランスパイル後のファイルの先頭に挿入される
	"""

	def __call__(self, module_path: ModulePath) -> str:
		"""メタヘッダーを生成

		Args:
			module_path (ModulePath): モジュールパス
		Returns:
			str: メタヘッダー
		"""
		...


class ITranslator(metaclass=ABCMeta):
	"""トランスレーターインターフェイス"""

	@property
	@abstractmethod
	def version(self) -> str:
		"""str: バージョン"""
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
