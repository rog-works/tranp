from rogw.tranp.dsn.dsn import DSN


def alias_dsn(fullyname: str) -> str:
	"""エイリアス用のDSNに変換

	Args:
		fullyname: 完全参照名
	Returns:
		DSN
	Note:
		# エイリアス用DSNの書式
		例: 'aliases.module.path.to.symbol'
	"""
	return DSN.join('aliases', fullyname)


def import_dsn(module_path: str) -> str:
	"""インポート用のDSNに変換

	Args:
		module_path: モジュールパス
	Returns:
		DSN
	Note:
		# インポート用DSNの書式
		例: 'imports.module.path'
	"""
	return DSN.join('imports', module_path)
