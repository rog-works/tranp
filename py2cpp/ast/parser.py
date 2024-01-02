from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from py2cpp.ast.entry import Entry


@dataclass
class ParserSetting:
	"""シンタックスパーサー設定データ

	Attributes:
		grammer (str): Grammarファイルへのパス(実行ディレクトリーからの相対パス)
		start (str): ルートエントリータグ(default = 'file_input')
		algorithem (str): パーサーアルゴリズム(default = 'lalr')
	"""

	grammar: str
	start: str = 'file_input'
	algorithem: str = 'lalr'


class SyntaxParser(metaclass=ABCMeta):
	"""シンタックスパーサーのインターフェイス。Grammarの定義を元にソースを解析し、シンタックスツリーを生成する機能を提供"""

	@abstractmethod
	def parse(self, module_path: str) -> Entry:
		"""モジュールを解析してシンタックスツリーを生成

		Args:
			module_path (str): モジュールパス
		Returns:
			Entry: シンタックスツリーのルートエントリー
		"""
		raise NotImplementedError()
