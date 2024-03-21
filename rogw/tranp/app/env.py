import os
from typing import Any

from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.lang.dict import deep_merge


class Env:
	"""環境変数

	Note:
		実行ディレクトリーとPythonのコアライブラリーのパスは必ず通った設定になる
	"""

	def __init__(self, env: dict[str, Any]) -> None:
		"""インスタンスを生成

		Args:
			env (dict[str, Any]): 環境変数データ
		"""
		self.__env = deep_merge(self.__default_env(), env)

	def __default_env(self) -> dict[str, Any]:
		"""環境変数のデフォルトデータを生成

		Returns:
			dict[str, Any]: 環境変数データ
		"""
		paths = [
			os.getcwd(),
			os.path.join(tranp_dir(), 'rogw/tranp/compatible/libralies'),
		]
		return {'PYTHONPATH': {path: path for path in paths}}

	@property
	def paths(self) -> list[str]:
		"""list[str]: パスリスト"""
		return self.__env['PYTHONPATH'].values()
