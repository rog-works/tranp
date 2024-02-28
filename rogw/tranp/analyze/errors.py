from rogw.tranp.errors import Error


class LexicalError(Error):
	"""意味解析由来のエラー"""
	pass

class UnresolvedSymbolError(LexicalError):
	"""シンボルの解決に失敗

	Note:
		# SymbolNotDefinedErrorとの相違点
		* SymbolNotDefinedErrorは検索のみが対象
		* UnresolvedSymbolErrrorはシンボル解決に関わるあらゆる事柄を内包
	"""
	pass

class MustBeImplementedError(LexicalError):
	"""必須の機能(クラス/ファンクション)の実装漏れ"""
	pass

class SymbolNotDefinedError(LexicalError):
	"""未定義のシンボルを検索"""
	pass

class OperationNotAllowedError(LexicalError):
	"""シンボル同士の許可されない(または未実装)の演算を指定"""
	pass

class ProcessingError(LexicalError):
	"""意味解析中の未特定の実行エラー"""
	pass
