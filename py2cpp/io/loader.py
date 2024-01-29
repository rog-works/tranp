import os

from py2cpp.app.env import Env  # FIXME appに依存するのはNG。インターフェイスと実装の分離を検討


class FileLoader:
	"""ファイルローダー"""

	def __init__(self, env: Env) -> None:
		"""インスタンスを生成

		Args:
			env (Env): 環境変数
		"""
		self.__env = env

	def load(self, filepath: str) -> str:
		"""ファイルをロード

		Args:
			filepath (str): 実行ディレクトリーからの相対パス
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

	def mtime(self, filepath: str) -> float:
		"""ファイルの最終更新日時を取得

		Args:
			filepath (str): 実行ディレクトリーからの相対パス
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
