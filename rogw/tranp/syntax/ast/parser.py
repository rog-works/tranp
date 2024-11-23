from dataclasses import dataclass
from typing import Protocol

from rogw.tranp.syntax.ast.entry import Entry


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


class SyntaxParser(Protocol):
	"""シンタックスパーサープロトコル。Grammarの定義を元にソースを解析し、シンタックスツリーを生成"""

	def __call__(self, module_path: str) -> Entry:
		"""モジュールを解析してシンタックスツリーを生成

		Args:
			module_path (str): モジュールパス
		Returns:
			Entry: シンタックスツリーのルートエントリー
		"""
		...


class SourceProvider(Protocol):
	"""ソースコードプロバイダープロトコル"""

	def __call__(self, module_path: str) -> str:
		"""モジュールパスを基にソースコードを生成

		Args:
			module_path (str): モジュールパス
		Returns:
			str: ソースコード
		"""
		...
