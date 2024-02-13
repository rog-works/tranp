import os

from rogw.tranp.app.env import Env
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.implementation import implements, injectable


def appdir() -> str:
	"""アプリケーションのルートディレクトリーを取得

	Returns:
		str: ルートディレクトリーの絶対パス
	Note:
		このモジュールを起点にルートディレクトリーを算出
	"""
	return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))


class FileLoader(IFileLoader):
	"""ファイルローダー"""

	@injectable
	def __init__(self, env: Env) -> None:
		"""インスタンスを生成

		Args:
			env (Env): 環境変数 @inject
		"""
		self.__env = env

	@implements
	def load(self, filepath: str) -> str:
		"""ファイルをロード

		Args:
			filepath (str): 実行ディレクトリーからの相対パス。または絶対パス
		Returns:
			str: コンテンツ
		Raises:
			FileNotFoundError: 存在しないファイルを指定
		"""
		found_filepath = self.__resolve_filepath(filepath)
		if found_filepath is None:
			raise FileNotFoundError(f'No such file or directory. filepath: {filepath}')

		with open(found_filepath, mode='r', encoding='utf-8') as f:
			return '\n'.join(f.readlines())

	@implements
	def mtime(self, filepath: str) -> float:
		"""ファイルの最終更新日時を取得

		Args:
			filepath (str): 実行ディレクトリーからの相対パス。または絶対パス
		Returns:
			float: タイムスタンプ
		Raises:
			FileNotFoundError: 存在しないファイルを指定
		"""
		found_filepath = self.__resolve_filepath(filepath)
		if found_filepath is None:
			raise FileNotFoundError(f'No such file or directory. filepath: {filepath}')

		return os.path.getmtime(found_filepath)

	def __resolve_filepath(self, filepath: str) -> str | None:
		"""ファイルパスを解決。未検出の場合はNoneを返却

		Args:
			filepath (str): 実行ディレクトリーからの相対パス
		Returns:
			str | None: 解決したファイルパス
		Note:
			環境変数のPYTHONPATHの登録順に探索
		"""
		for path in self.__env.paths:
			abs_filepath = os.path.abspath(os.path.join(path, filepath))
			if os.path.isfile(abs_filepath):
				return abs_filepath

		return None
