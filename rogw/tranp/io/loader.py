from abc import ABCMeta, abstractmethod


class IFileLoader(metaclass=ABCMeta):
	"""ファイルローダーインターフェイス"""

	@abstractmethod
	def exists(self, filepath: str) -> bool:
		"""ファイルが存在するか判定

		Args:
			filepath (str): 実行ディレクトリーからの相対パス。または絶対パス
		Returns:
			bool: True = 存在する
		"""
		...

	@abstractmethod
	def load(self, filepath: str) -> str:
		"""ファイルをロード

		Args:
			filepath (str): 実行ディレクトリーからの相対パス。または絶対パス
		Returns:
			str: コンテンツ
		Raises:
			FileNotFoundError: 存在しないファイルを指定
		"""
		...

	@abstractmethod
	def mtime(self, filepath: str) -> float:
		"""ファイルの最終更新日時を取得

		Args:
			filepath (str): 実行ディレクトリーからの相対パス。または絶対パス
		Returns:
			float: タイムスタンプ
		Raises:
			FileNotFoundError: 存在しないファイルを指定
		"""
		...
