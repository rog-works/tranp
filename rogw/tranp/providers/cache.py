from rogw.tranp.cache.cache import CacheSetting


def cache_setting() -> CacheSetting:
	"""キャッシュ設定データを生成

	Returns:
		キャッシュ設定データ
	"""
	return CacheSetting(basedir='.cache/tranp')
