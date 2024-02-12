from tranp.io.cache import CacheSetting


def cache_setting() -> CacheSetting:
	return CacheSetting(basedir='.cache/tranp')
