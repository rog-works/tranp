from rogw.tranp.i18n.i18n import TranslationMapping


def translation_mapping() -> TranslationMapping:
	"""翻訳マッピングデータを生成

	Returns:
		I18nMapping: 翻訳マッピングデータ
	"""
	return TranslationMapping(to={
		'aliases.rogw.tranp.compatible.python.classes.String': 'std::string',
		'aliases.rogw.tranp.compatible.python.classes.List': 'std::vector',
		'aliases.rogw.tranp.compatible.python.classes.Dict': 'std::map',
	})
