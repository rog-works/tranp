import re
from typing import Any, Protocol, Union, TypedDict

from jinja2 import Environment, FileSystemLoader

from rogw.tranp.dsn.translation import alias_dsn


class Translator(Protocol):
	"""翻訳関数プロトコル

	Note:
		@see tranp.i18n.i18n.I18n.t
	"""

	def __call__(self, key: str) -> str:
		"""翻訳キーに対応する文字列に変換

		Args:
			key (str): 翻訳キー
		Returns:
			str: 翻訳後の文字列
		"""
		...


class Renderer:
	"""テンプレートレンダー"""

	def __init__(self, template_dirs: list[str], translator: Translator) -> None:
		"""インスタンスを生成

		Args:
			template_dirs (list[str]): テンプレートファイルのディレクトリーリスト
			translator (Translator): 翻訳関数
		"""
		self.__renderer = Environment(loader=FileSystemLoader(template_dirs, encoding='utf-8'))
		self.__renderer.globals['i18n'] = lambda prefix, key: translator(f'{translator(alias_dsn(prefix))}.{key}')
		self.__renderer.globals['reg_match'] = lambda pattern, string: re.search(pattern, string)
		self.__renderer.globals['reg_fullmatch'] = lambda pattern, string: re.fullmatch(pattern, string)
		self.__renderer.globals['reg_replace'] = lambda pattern, replace, string: re.sub(pattern, replace, string)

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
