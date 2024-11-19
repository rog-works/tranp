from typing import Any, Callable, Literal, NamedTuple, Protocol, TypeAlias

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


RendererHelperFactory: TypeAlias = Callable[[RendererSetting], Callable[..., Any]]


class RendererHelperProvider(Protocol):
	"""ヘルパープロバイダープロトコル

	Returns:
		dict[Literal['function', 'filter'], dict[str, Callable[..., Any]]]: ヘルパー一覧({登録タイプ: {関数名: ヘルパー関数}})
	"""

	def __call__(self) -> dict[Literal['function', 'filter'], dict[str, Callable[..., Any]]]:
		"""@see decl"""
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
				if tag == 'function':
					self.__renderer.globals[name] = helper
				elif tag == 'filter':
					self.__renderer.filters[name] = helper

	def render(self, template: str, vars: dict[str, Any] = {}) -> str:
		"""テンプレートをレンダリング

		Args:
			template (str): テンプレートファイルの名前
			vars (dict[str, Any]) テンプレートへの入力変数(default = {})
		Returns:
			str: レンダリング結果
		"""
		return self.__renderer.get_template(f'{template}.j2').render(vars)
