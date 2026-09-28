from typing import cast

import yaml

from tranp.app.file.loader import IDataLoader
from tranp.app.i18n.i18n import TranslationMapping


def translation_mapping_cpp(datums: IDataLoader) -> TranslationMapping:
	"""翻訳マッピングデータを生成(C++用)

	Args:
		datums: データローダー
	Returns:
		翻訳マッピングデータ
	"""
	mapping = cast(dict[str, str], yaml.safe_load(datums.load('data/i18n.yml')))
	return TranslationMapping(to=mapping)
