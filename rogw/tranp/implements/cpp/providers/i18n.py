from typing import cast

import yaml

from rogw.tranp.i18n.i18n import TranslationMapping
from rogw.tranp.io.loader import IFileLoader


def translation_mapping_cpp(loader: IFileLoader) -> TranslationMapping:
	"""翻訳マッピングデータを生成

	Args:
		loader (IFileLoader): ファイルローダー
	Returns:
		TranslationMapping: 翻訳マッピングデータ
	"""
	mapping = cast(dict[str, str], yaml.safe_load(loader.load('data/cpp/i18n.yml')))
	return TranslationMapping(to=mapping)
