import os
import time


class Writer:
	"""ファイルライター"""

	def __init__(self, filepath: str) -> None:
		"""インスタンスを生成

		Args:
			filepath: 出力ファイルのパス
		"""
		self.__filepath = filepath
		self.__content = ''

	def put(self, text: str) -> None:
		"""バッファにテキストを出力

		Args:
			text: テキスト
		"""
		self.__content += text

	def flush(self) -> None:
		"""出力バッファをファイルに反映"""
		abs_filepath = os.path.abspath(self.__filepath)
		dirpath = os.path.dirname(abs_filepath)
		if not os.path.exists(dirpath):
			os.makedirs(dirpath)

		try:
			self._flush(abs_filepath)
		except PermissionError:
			# XXX 連続して出力すると稀にエラーが発生するため、若干間隔を空けて再出力を試行
			time.sleep(0.1)
			self._flush(abs_filepath)

	def _flush(self, filepath: str) -> None:
		"""出力バッファをファイルに反映

		Args:
			filepath: 出力パス
		"""
		with open(filepath, mode='wb') as f:
			f.write(self.__content.encode('utf-8'))
