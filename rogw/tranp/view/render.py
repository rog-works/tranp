from typing import Any, Union, TypedDict

from jinja2 import Environment, FileSystemLoader



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
		text = self.__renderer.get_template(f'{template}.j2').render(vars)
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
