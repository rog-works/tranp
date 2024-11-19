import os
from typing import TypedDict, cast

from rogw.tranp.app.dir import tranp_dir
from rogw.tranp.lang.dict import dict_merge

EnvDict = TypedDict('EnvDict', {'PYTHONPATH': dict[str, str]})


class Env:
	"""環境変数

	Note:
		実行ディレクトリーとPythonのコアライブラリーのパスは必ず通った設定になる
	"""

	def __init__(self, env: EnvDict) -> None:
		"""インスタンスを生成

		Args:
			env (EnvDict): 環境変数データ
		"""
		self.__env = cast(EnvDict, dict_merge(cast(dict, self.__default_env()), cast(dict, env)))

	def __default_env(self) -> EnvDict:
		"""環境変数のデフォルトデータを生成

		Returns:
			EnvDict: 環境変数データ
		"""
		paths = [
			os.getcwd(),
			os.path.join(tranp_dir(), 'rogw/tranp/compatible/libralies'),
		]
		return {'PYTHONPATH': {path: path for path in paths}}

	@property
	def paths(self) -> list[str]:
		"""list[str]: パスリスト"""
		return list(self.__env['PYTHONPATH'].values())
