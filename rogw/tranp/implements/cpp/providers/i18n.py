from rogw.tranp.i18n.i18n import TranslationMapping


def translation_mapping() -> TranslationMapping:
	"""翻訳マッピングデータを生成

	Returns:
		I18nMapping: 翻訳マッピングデータ
	"""
	return TranslationMapping(to={
		'aliases.rogw.tranp.compatible.python.classes.str': 'std::string',
		'aliases.rogw.tranp.compatible.python.classes.list': 'std::vector',
		'aliases.rogw.tranp.compatible.python.classes.list.append': 'push_back',
		'aliases.rogw.tranp.compatible.python.classes.dict': 'std::map',
	})
