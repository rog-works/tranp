from typing import Any, Callable, NamedTuple, Protocol

from jinja2 import Environment, FileSystemLoader

from rogw.tranp.lang.translator import Translator


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


class RendererHelperProvider(Protocol):
	"""ヘルパープロバイダープロトコル

	Returns:
		dict[str, dict[str, Callable[..., Any]]]: ヘルパー一覧({登録タイプ: {関数名: ヘルパー関数}})
	"""

	def __call__(self) -> dict[str, dict[str, Callable[..., Any]]]:
		...


class Renderer:
	"""テンプレートレンダー"""

	def __init__(self, setting: RendererSetting, helper_provider: RendererHelperProvider) -> None:
		"""インスタンスを生成

		Args:
			setting (RendererSetting): テンプレートレンダー設定データ
			helper_privider (RendererHelperProvider): ヘルパープロバイダー
		"""
		self.__renderer = Environment(loader=FileSystemLoader(setting.template_dirs, encoding='utf-8'), auto_reload=False)
		for tag, helpers in helper_provider().items():
			for name, helper in helpers.items():
				if tag == 'globals':
					self.__renderer.globals[name] = helper
				elif tag == 'filters':
					self.__renderer.filters[name] = helper

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
