from rogw.tranp.syntax.ast.dsn import DSN


def alias_dsn(fullyname: str) -> str:
	"""エイリアス用のDSNに変換

	Args:
		fullyname (str): 完全参照名
	Returns:
		str: DSN
	Note:
		# エイリアス用DSNの書式
		例: 'aliases.module.path.to.symbol'
	"""
	return DSN.join('aliases', fullyname)


def import_dsn(module_path: str) -> str:
	"""インポート用のDSNに変換

	Args:
		module_path (str): モジュールパス
	Returns:
		str: DSN
	Note:
		# インポート用DSNの書式
		例: 'imports.module.path'
	"""
	return DSN.join('imports', module_path)


def to_classes_alias(key: str) -> str:
	"""標準ライブラリーのエイリアスDSNに変換

	Args:
		key (str): キー名
	Returns:
		str: DSN
	"""
	return alias_dsn(f'rogw.tranp.compatible.libralies.classes.{key}')


def to_cpp_alias(key: str) -> str:
	"""C++のエイリアスDSNに変換 FIXME C++に直接依存するのはNG

	Args:
		key (str): キー名
	Returns:
		str: DSN
	"""
	return alias_dsn(f'rogw.tranp.compatible.cpp.classes.{key}')
