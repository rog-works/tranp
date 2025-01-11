import hashlib
import os

from rogw.tranp.file.loader import IFileLoader
from rogw.tranp.lang.annotation import implements


class FileLoader(IFileLoader):
	"""ファイルローダー"""

	def __init__(self, env_paths: list[str]) -> None:
		"""インスタンスを生成

		Args:
			env_paths: 環境パスリスト @inject
		"""
		self.__env_paths = env_paths
		self.__hashs: dict[str, str] = {}
		self.__mtimes: dict[str, float] = {}

	@implements
	def exists(self, filepath: str) -> bool:
		"""ファイルが存在するか判定

		Args:
			filepath: 実行ディレクトリーからの相対パス。または絶対パス
		Returns:
			bool: True = 存在する
		"""
		return self.__resolve_filepath(filepath) is not None

	@implements
	def load(self, filepath: str) -> str:
		"""ファイルをロード

		Args:
			filepath: 実行ディレクトリーからの相対パス。または絶対パス
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
			filepath: 実行ディレクトリーからの相対パス。または絶対パス
		Returns:
			float: タイムスタンプ
		Raises:
			FileNotFoundError: 存在しないファイルを指定
		"""
		found_filepath = self.__resolve_filepath(filepath)
		if found_filepath is None:
			raise FileNotFoundError(f'No such file or directory. filepath: {filepath}')

		if found_filepath not in self.__mtimes:
			self.__mtimes[found_filepath] = os.path.getmtime(found_filepath)

		return self.__mtimes[found_filepath]

	@implements
	def hash(self, filepath: str) -> str:
		"""ファイルのハッシュ値を取得

		Args:
			filepath: 実行ディレクトリーからの相対パス。または絶対パス
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
			filepath: 実行ディレクトリーからの相対パス。または絶対パス
		Returns:
			str | None: 解決したファイルパス
		Note:
			環境変数のPYTHONPATHの登録順に探索
		"""
		if os.path.isabs(filepath):
			return filepath if os.path.isfile(filepath) else None

		for path in self.__env_paths:
			abs_filepath = os.path.abspath(os.path.join(path, filepath))
			if os.path.isfile(abs_filepath):
				return abs_filepath

		return None
