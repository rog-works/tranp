from rogw.tranp.errors import Error


class SemanticsError(Error):
	"""意味解析由来のエラー"""
	pass

class UnresolvedSymbolError(SemanticsError):
	"""シンボルの解決に失敗

	Note:
		# SymbolNotDefinedErrorとの相違点
		* SymbolNotDefinedErrorは検索のみが対象
		* UnresolvedSymbolErrrorはシンボル解決に関わるあらゆる事柄を内包
	"""
	pass

class MustBeImplementedError(SemanticsError):
	"""必須の機能(クラス/ファンクション)の実装漏れ"""
	pass

class SymbolNotDefinedError(SemanticsError):
	"""未定義のシンボルを検索"""
	pass

class OperationNotAllowedError(SemanticsError):
	"""シンボル同士の許可されない(または未実装)の演算を指定"""
	pass

class ProcessingError(SemanticsError):
	"""意味解析中の未特定の実行エラー"""
	pass
