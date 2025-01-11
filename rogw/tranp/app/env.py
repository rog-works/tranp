import os

from rogw.tranp.app.dir import tranp_dir


class DataEnvPath(list[str]):
	"""環境パスリスト(データ用)

	Note:
		### デフォルトのパス
		* 実行ディレクトリー
		### パスの追加の必要性
		* 追加する必要性はほぼ無いため、デフォルトの設定を使うことを推奨
	"""

	@classmethod
	def instantiate(cls) -> 'DataEnvPath':
		"""インスタンスを生成

		Returns:
			インスタンス
		"""
		return cls([os.getcwd()])


class SourceEnvPath(list[str]):
	"""環境パスリスト(ソースコード用)

	Note:
		### デフォルトのパス
		* 実行ディレクトリー
		* tranpのルートディレクトリー
		* Pythonライブラリーのディレクトリー
		### パスの追加の必要性
		* 追加する必要性はほぼ無いため、デフォルトの設定を使うことを推奨
	"""

	@classmethod
	def instantiate(cls, input_dirs: list[str]) -> 'SourceEnvPath':
		"""インスタンスを生成

		Args:
			input_dirs: 入力ディレクトリーリスト
		Returns:
			インスタンス
		"""
		default_dirs = [os.getcwd(), tranp_dir(), os.path.join(tranp_dir(), 'rogw/tranp/compatible/libralies')]
		return cls([*default_dirs, *input_dirs])
