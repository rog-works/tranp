from typing import cast

import yaml

from rogw.tranp.i18n.i18n import TranslationMapping
from rogw.tranp.file.loader import IDataLoader


def translation_mapping_cpp_example(datums: IDataLoader) -> TranslationMapping:
	"""翻訳マッピングデータを生成(example用)

	Args:
		datums: データローダー
	Returns:
		翻訳マッピングデータ
	"""
	mapping = cast(dict[str, str], yaml.safe_load(datums.load('data/i18n.yml')))
	return TranslationMapping(to=mapping)
