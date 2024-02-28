from rogw.tranp.errors import Error


class LexError(Error):
	"""意味解析由来のエラー"""
	pass

class UnresolvedSymbolError(LexError):
	"""シンボルの解決に失敗"""
	pass

class ImplementationError(LexError):
	"""必須の機能(クラス/ファンクション)の実装漏れ"""
	pass

class SymbolNotDefinedError(LexError):
	"""未定義のシンボルを検索"""
	pass

class OperationNotAllowedError(LexError):
	"""許可されない(または未実装)の演算を指定"""
	pass

class ProcessingError(LexError):
	"""意味解析中の未特定の実行エラー"""
	pass
