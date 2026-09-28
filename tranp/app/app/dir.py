import os


def repository_dir() -> str:
	"""リポジトリーのルートディレクトリーを取得

	Returns:
		ルートディレクトリーの絶対パス
	Note:
		このモジュールを起点にルートディレクトリーを算出
	"""
	return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))


def tranp_dir() -> str:
	"""tranpディレクトリーを取得

	Returns:
		tranpディレクトリーの絶対パス
	"""
	return os.path.join(repository_dir(), 'tranp')
