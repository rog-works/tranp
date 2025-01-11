from typing import NamedTuple

from rogw.tranp.lang.annotation import duck_typed
from rogw.tranp.lang.translator import Translator


class TranslationMapping(NamedTuple):
	"""翻訳マッピングデータ

	Attributes:
		to: {翻訳キー: 翻訳後}
	"""

	to: dict[str, str] = {}

	def merge(self, to: dict[str, str]) -> 'TranslationMapping':
		"""追加のマッピングデータとマージ

		Args:
			to: {翻訳キー: 翻訳後}
		Returns:
			TranslationMapping: インスタンス
		"""
		return TranslationMapping(to={**self.to, **to})


class I18n:
	"""国際化対応モジュール"""

	def __init__(self, translation: TranslationMapping) -> None:
		"""インスタンスを生成
		
		Args:
			translation: 翻訳マッピングデータ
		"""
		self.__translation = translation

	@duck_typed(Translator)
	def t(self, key: str, fallback: str = '') -> str:
		"""翻訳キーに対応する文字列に変換

		Args:
			key: 翻訳キー
			fallback: 存在しない場合の代用値(default = '')
		Returns:
			str: 翻訳後の文字列
		"""
		return self.__translation.to.get(key, fallback)


def translation_mapping_empty() -> TranslationMapping:
	"""翻訳マッピングデータを生成(空)

	Returns:
		TranslationMapping: 翻訳マッピングデータ
	"""
	return TranslationMapping(to={})
