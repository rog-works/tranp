import os

from rogw.tranp.app.dir import tranp_dir


class DataEnvPath(list[str]):
	"""環境パスリスト(データ用)"""

	@classmethod
	def instantiate(cls) -> 'DataEnvPath':
		"""インスタンスを生成

		Returns:
			DataEnvPath: インスタンス
		"""
		return cls([os.getcwd()])


class SourceEnvPath(list[str]):
	"""環境パスリスト(ソースコード用)"""

	@classmethod
	def instantiate(cls, input_dirs: list[str]) -> 'SourceEnvPath':
		"""インスタンスを生成

		Args:
			input_dirs: 入力ディレクトリーリスト
		Returns:
			SourceEnvPath: インスタンス
		"""
		default_dirs = [
			tranp_dir(),
			os.path.join(tranp_dir(), 'rogw/tranp/compatible/libralies'),
		]
		return cls([*default_dirs, *input_dirs])
