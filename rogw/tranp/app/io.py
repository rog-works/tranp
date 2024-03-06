import hashlib
import os

from rogw.tranp.app.env import Env
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.annotation import implements, injectable


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
		self.__hashs: dict[str, str] = {}

	@implements
	def exists(self, filepath: str) -> bool:
		"""ファイルが存在するか判定

		Args:
			filepath (str): 実行ディレクトリーからの相対パス。または絶対パス
		Returns:
			bool: True = 存在する
		"""
		return self.__resolve_filepath(filepath) is not None

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

		with open(found_filepath, mode='rb') as f:
			content_bytes = f.read()
			self.__hashs[found_filepath] = hashlib.md5(content_bytes).hexdigest()
			return content_bytes.decode('utf-8')

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

	@implements
	def hash(self, filepath: str) -> str:
		"""ファイルのハッシュ値を取得

		Args:
			filepath (str): 実行ディレクトリーからの相対パス。または絶対パス
		Returns:
			str: ハッシュ値
		Raises:
			FileNotFoundError: 存在しないファイルを指定
		"""
		found_filepath = self.__resolve_filepath(filepath)
		if found_filepath is None:
			raise FileNotFoundError(f'No such file or directory. filepath: {filepath}')

		# XXX ハッシュ値をキャッシュさせるためにロードを実行
		if found_filepath not in self.__hashs:
			self.load(found_filepath)

		return self.__hashs[found_filepath]

	def __resolve_filepath(self, filepath: str) -> str | None:
		"""ファイルパスを解決。未検出の場合はNoneを返却

		Args:
			filepath (str): 実行ディレクトリーからの相対パス。または絶対パス
		Returns:
			str | None: 解決したファイルパス
		Note:
			環境変数のPYTHONPATHの登録順に探索
		"""
		if os.path.isabs(filepath):
			return filepath

		for path in self.__env.paths:
			abs_filepath = os.path.abspath(os.path.join(path, filepath))
			if os.path.isfile(abs_filepath):
				return abs_filepath

		return None
