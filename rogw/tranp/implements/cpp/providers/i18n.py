from rogw.tranp.i18n.i18n import TranslationMapping


def translation_mapping() -> TranslationMapping:
	"""翻訳マッピングデータを生成

	Returns:
		TranslationMapping: 翻訳マッピングデータ
	"""
	return TranslationMapping(to={
		'aliases.rogw.tranp.compatible.libralies.classes.str': 'std::string',
		'aliases.rogw.tranp.compatible.libralies.classes.list': 'std::vector',
		'aliases.rogw.tranp.compatible.libralies.classes.list.append': 'push_back',
		'aliases.rogw.tranp.compatible.libralies.classes.dict': 'std::map',
	})
