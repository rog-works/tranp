from rogw.tranp.io.cache import CacheSetting


def cache_setting() -> CacheSetting:
	"""キャッシュ設定データを生成

	Returns:
		CacheSetting: キャッシュ設定データ
	"""
	return CacheSetting(basedir='.cache/tranp')
