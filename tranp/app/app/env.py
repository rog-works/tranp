import os

from tranp.app.app.dir import repository_dir, tranp_dir


class DataEnvPath:
	"""環境パスリスト(データ用)

	Note:
		```
		### デフォルトのパス
		* 実行ディレクトリー
		### パスの追加の必要性
		* 追加する必要性はほぼ無いため、デフォルトの設定を使うことを推奨
		```
	"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.paths = [os.getcwd()]


class SourceEnvPath:
	"""環境パスリスト(ソースコード用)

	Note:
		```
		### デフォルトのパス
		* 実行ディレクトリー
		* Pythonライブラリーのディレクトリー
		* リポジトリーのディレクトリー
		### パスの追加の必要性
		* 追加する必要性はほぼ無いため、デフォルトの設定を使うことを推奨
		```
	"""

	def __init__(self) -> None:
		"""インスタンスを生成"""
		self.paths = [os.getcwd(), os.path.join(tranp_dir(), 'app', 'compatible', 'libralies'), repository_dir()]
