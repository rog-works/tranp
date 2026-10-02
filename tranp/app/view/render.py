import os
from typing import Any, Callable, NamedTuple, Protocol, TypeAlias

from jinja2 import Environment, FileSystemLoader

from tranp.app.app.env import DataEnvPath
from tranp.app.lang.middleware import Middleware
from tranp.app.lang.translator import Translator

RendererEmitter: TypeAlias = Middleware


class RendererSetting(NamedTuple):
	"""テンプレートレンダー設定データ

	Attributes:
		template_dirs: テンプレートの入力ディレクトリーリスト(相対/絶対)
		translator: 翻訳関数
		emitter: レンダー用イベントエミッター
		env: 環境変数
	"""
	template_dirs: list[str]
	translator: Translator
	emitter: RendererEmitter
	env: dict[str, Any]


RendererHelperFactory: TypeAlias = Callable[[RendererSetting], Callable[..., Any]]


class RendererHelperProvider(Protocol):
	"""ヘルパープロバイダープロトコル

	Returns:
		([ヘルパーファクトリー(関数)], [ヘルパーファクトリー(フィルター)])
	"""

	def __call__(self) -> tuple[list[RendererHelperFactory], list[RendererHelperFactory]]:
		"""@see decl"""
		...


class Renderer:
	"""テンプレートレンダー"""

	def __init__(self, env_path: DataEnvPath, setting: RendererSetting, helper_provider: RendererHelperProvider) -> None:
		"""インスタンスを生成

		Args:
			env_path: 環境パスリスト(データ用)
			setting: テンプレートレンダー設定データ
			helper_privider: ヘルパープロバイダー
		"""
		template_dirs = self.__make_template_dirs(env_path, setting)
		self.__renderer = Environment(loader=FileSystemLoader(template_dirs, encoding='utf-8'), auto_reload=False)
		self.__apply_helpers(setting, helper_provider)

	def __make_template_dirs(self, env_path: DataEnvPath, setting: RendererSetting) -> list[str]:
		"""テンプレートの入力ディレクトリーリストを生成

		Args:
			env_path: 環境パス(データ用)
			setting: テンプレートレンダー設定データ
		Returns:
			入力ディレクトリーリスト
		"""
		template_dirs: list[str] = []
		for in_path in env_path.paths:
			for template_dir in setting.template_dirs:
				in_template_dir = os.path.abspath(os.path.join(in_path, template_dir))
				if os.path.exists(in_template_dir):
					template_dirs.append(in_template_dir)

		return template_dirs

	def __apply_helpers(self, setting: RendererSetting, helper_provider: RendererHelperProvider) -> None:
		"""テンプレートヘルパーを適用

		Args:
			helper_privider: ヘルパープロバイダー
		"""
		for index, factories in enumerate(helper_provider()):
			for factory in factories:
				if index == 0:
					self.__renderer.globals[factory.__name__] = factory(setting)
				elif index == 1:
					self.__renderer.filters[factory.__name__] = factory(setting)

	def render(self, template: str, vars: dict[str, Any] = {}) -> str:
		"""テンプレートをレンダリング

		Args:
			template: テンプレートファイルの名前
			vars (dict[str, Any]) テンプレートへの入力変数(default = {})
		Returns:
			レンダリング結果
		"""
		return self.__renderer.get_template(f'{template}.j2').render(vars)
