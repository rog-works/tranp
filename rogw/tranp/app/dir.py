import os


def tranp_dir() -> str:
	"""Tranpのルートディレクトリーを取得

	Returns:
		str: Tranpのルートディレクトリーの絶対パス
	Note:
		このモジュールを起点にルートディレクトリーを算出
	"""
	return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
