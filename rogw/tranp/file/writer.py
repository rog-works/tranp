import os


class Writer:
	"""ファイルライター"""

	def __init__(self, filepath: str) -> None:
		"""インスタンスを生成

		Args:
			filepath (str): 出力ファイルのパス
		"""
		self.__filepath = filepath
		self.__content = ''

	def put(self, text: str) -> None:
		"""バッファにテキストを出力

		Args:
			text (str): テキスト
		"""
		self.__content += text

	def flush(self) -> None:
		"""出力バッファをファイルに反映"""
		abs_filepath = os.path.abspath(self.__filepath)
		dirpath = os.path.dirname(abs_filepath)
		if not os.path.exists(dirpath):
			os.makedirs(dirpath)

		with open(abs_filepath, mode='wb') as f:
			f.write(self.__content.encode('utf-8'))
