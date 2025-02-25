from typing import Protocol


class Translator(Protocol):
	"""翻訳関数プロトコル"""

	def __call__(self, key: str, fallback: str = '') -> str:
		"""翻訳キーに対応する文字列に変換

		Args:
			key: 翻訳キー
			fallback: 存在しない場合の代用値(default = '')
		Returns:
			翻訳後の文字列
		"""
		...
