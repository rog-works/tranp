from typing import Any, Union, TypedDict

from jinja2 import Environment, FileSystemLoader


class Writer:
	"""ファイルライター"""

	def __init__(self, filepath: str) -> None:
		"""インスタンスを生成

		Args:
			filepath (str): 出力ファイルのパス
		"""
		self.__filepath = filepath
		self.__content = ''

	def put(self, text: str) -> None:
		"""バッファにテキストを出力

		Args:
			text (str): テキスト
		"""
		self.__content += text

	def flush(self) -> None:
		"""出力バッファをファイルに反映"""
		with open(self.__filepath, mode='wb') as f:
			f.write(self.__content.encode('utf-8'))


class Renderer:
	"""テンプレートレンダー"""

	def __init__(self, template_dir: str) -> None:
		"""インスタンスを生成

		Args:
			template_dir (str): テンプレートファイルのディレクトリー
		"""
		self.__renderer = Environment(loader=FileSystemLoader(template_dir, encoding='utf-8'))

	def render(self, template: str, indent: int = 0, vars: Union[TypedDict, dict[str, Any]] = {}) -> str:
		"""テンプレートをレンダリング

		Args:
			template (str): テンプレートファイルの名前
			indent (int): インデント(default = 0)
			vars (Union[TypedDict, dict[str, Any]]) テンプレートへの入力変数(default = {})
		Returns:
			str: レンダリング結果
		"""
		text = self.__renderer.get_template(template).render(vars)
		return self.__indentation(text, indent)

	def __indentation(self, text: str, indent: int) -> str:
		"""レンダリング結果にインデントを加える

		Args:
			text (str): レンダリング結果
			indent (int): インデント
		Returns:
			str: 変更結果
		"""
		if indent == 0:
			return text

		begin = '\t' * indent
		return begin + f'\n{begin}'.join(text.split('\n'))
