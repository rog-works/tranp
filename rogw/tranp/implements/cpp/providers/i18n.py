from typing import cast

import yaml

from rogw.tranp.i18n.i18n import TranslationMapping
from rogw.tranp.file.loader import IDataLoader


def example_translation_mapping_cpp(datums: IDataLoader) -> TranslationMapping:
	"""翻訳マッピングデータを生成(example用)

	Args:
		datums (IDataLoader): データローダー
	Returns:
		TranslationMapping: 翻訳マッピングデータ
	"""
	mapping = cast(dict[str, str], yaml.safe_load(datums.load('example/data/i18n.yml')))
	return TranslationMapping(to=mapping)
