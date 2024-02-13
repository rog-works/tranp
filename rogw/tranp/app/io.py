import os


def appdir() -> str:
	"""アプリケーションのルートディレクトリーを取得

	Returns:
		str: ルートディレクトリーの絶対パス
	Note:
		このモジュールを起点にルートディレクトリーを算出
	"""
	return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
