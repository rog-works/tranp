from typing import cast

import yaml

from rogw.tranp.i18n.i18n import TranslationMapping
from rogw.tranp.io.loader import IFileLoader


def example_translation_mapping_cpp(files: IFileLoader) -> TranslationMapping:
	"""翻訳マッピングデータを生成(example用)

	Args:
		files (IFileLoader): ファイルローダー
	Returns:
		TranslationMapping: 翻訳マッピングデータ
	"""
	mapping = cast(dict[str, str], yaml.safe_load(files.load('example/data/i18n.yml')))
	return TranslationMapping(to=mapping)
