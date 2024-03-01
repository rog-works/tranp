from rogw.tranp.errors import Error


class SyntaxError(Error):
	"""シンタックス解析由来のエラー"""
	pass

class NodeNotFoundError(SyntaxError):
	"""指定したノードが存在しない"""
	pass

class UnresolvedNodeError(SyntaxError):
	"""ASTエントリーからノードの解決に失敗"""
	pass

class IllegalConvertionError(SyntaxError):
	"""派生クラスへの変換時に不正な変換先を指定"""
	pass

class InvalidRelationError(SyntaxError):
	"""ノード間の不正なリレーション"""
	pass
