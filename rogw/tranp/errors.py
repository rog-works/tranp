class Error(Exception):
	"""アプリケーション例外の基底クラス"""
	pass

class FatalError(Error):
	"""致命的なエラー"""
	pass

class LogicError(Error):
	"""実装不備"""
	pass

class NotFoundError(Error):
	"""データが存在しない"""
	pass
