import re
from typing import Any, NamedTuple

from jinja2 import Environment, FileSystemLoader

from rogw.tranp.dsn.module import ModuleDSN
from rogw.tranp.dsn.translation import alias_dsn
from rogw.tranp.lang.dict import dict_pluck
from rogw.tranp.lang.translator import Translator
from rogw.tranp.view.helper.block import BlockParser
from rogw.tranp.view.helper.decorator import DecoratorQuery
from rogw.tranp.view.helper.parameter import ParameterHelper


class RendererSetting(NamedTuple):
	"""テンプレートレンダー設定データ

	Attributes:
		template_dirs (list[str]): テンプレートファイルのディレクトリーリスト
		translator (Translator): 翻訳関数
		env: dict[str, Any]: 環境変数
	"""
	template_dirs: list[str]
	translator: Translator
	env: dict[str, Any]


class Renderer:
	"""テンプレートレンダー"""

	def __init__(self, setting: RendererSetting) -> None:
		"""インスタンスを生成

		Args:
			setting (RendererSetting): テンプレートレンダー設定データ
		"""
		self.__renderer = Environment(loader=FileSystemLoader(setting.template_dirs, encoding='utf-8'), auto_reload=False)
		self.__renderer.globals['break_last_block'] = lambda string, brackets: BlockParser.break_last_block(string, brackets)
		self.__renderer.globals['decorator_query'] = lambda decorators: DecoratorQuery.parse(decorators)
		self.__renderer.globals['env_get'] = lambda env_path, fallback: dict_pluck(setting.env, env_path, fallback)
		self.__renderer.globals['i18n'] = lambda module_path, local: setting.translator(ModuleDSN.full_joined(setting.translator(alias_dsn(module_path)), local))
		self.__renderer.globals['parameter_parse'] = lambda parameter: ParameterHelper.parse(parameter)
		self.__renderer.globals['reg_fullmatch'] = lambda pattern, string: re.fullmatch(pattern, string)
		self.__renderer.globals['reg_match'] = lambda pattern, string: re.search(pattern, string)
		self.__renderer.globals['reg_replace'] = lambda pattern, replace, string: re.sub(pattern, replace, string)
		self.__renderer.filters['filter_find'] = lambda strings, subject: [string for string in strings if string.find(subject) != -1]
		self.__renderer.filters['filter_replace'] = lambda strings, pattern, replace: [re.sub(pattern, replace, string) for string in strings]
		self.__renderer.filters['filter_match'] = lambda strings, pattern: [string for string in strings if re.search(pattern, string)]
		self.__renderer.filters['filter_fullmatch'] = lambda strings, pattern: [string for string in strings if re.fullmatch(pattern, string)]

	def render(self, template: str, indent: int = 0, vars: dict[str, Any] = {}) -> str:
		"""テンプレートをレンダリング

		Args:
			template (str): テンプレートファイルの名前
			indent (int): インデント(default = 0)
			vars (dict[str, Any]) テンプレートへの入力変数(default = {})
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
