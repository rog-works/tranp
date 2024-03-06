from rogw.tranp.syntax.ast.dsn import DSN


def alias_dsn(path: str) -> str:
	"""エイリアス用のDSNに変換

	Args:
		path (str): パス
	Returns:
		str: DSN
	"""
	return DSN.join('aliases', path)


def import_dsn(path: str) -> str:
	"""インポート用のDSNに変換

	Args:
		path (str): パス
	Returns:
		str: DSN
	"""
	return DSN.join('imports', path)
