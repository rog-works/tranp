from rogw.tranp.dsn.translation import alias_dsn, import_dsn
from rogw.tranp.i18n.i18n import TranslationMapping


def translation_mapping_cpp() -> TranslationMapping:
	"""翻訳マッピングデータを生成

	Returns:
		TranslationMapping: 翻訳マッピングデータ
	"""
	return TranslationMapping(to={
		# エイリアス
		alias_dsn('rogw.tranp.compatible.libralies.classes.str'): 'std::string',
		alias_dsn('rogw.tranp.compatible.libralies.classes.list'): 'std::vector',
		alias_dsn('rogw.tranp.compatible.libralies.classes.list.append'): 'push_back',
		alias_dsn('rogw.tranp.compatible.libralies.classes.dict'): 'std::map',
		# インポート
		import_dsn('example.FW.compatible'): '#include "FW/compatible.h"',
	})
