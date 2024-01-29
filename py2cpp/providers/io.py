from py2cpp.io.cache import CacheSetting


def cache_setting() -> CacheSetting:
	return CacheSetting(basedir='.cache/py2cpp')
