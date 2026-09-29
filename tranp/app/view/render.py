import os
from typing import Any, Callable, Literal, NamedTuple, Protocol, TypeAlias

from jinja2 import Environment, FileSystemLoader

from tranp.app.app.env import DataEnvPath
from tranp.app.lang.middleware import Middleware
from tranp.app.lang.translator import Translator

RendererEmitter: TypeAlias = Middleware


class RendererSetting(NamedTuple):
	"""テンプレートレンダー設定データ

	Attributes:
		template_dirs: テンプレートファイルのディレクトリーリスト
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
		ヘルパー一覧({登録タイプ: {関数名: ヘルパー関数}})
	"""

	def __call__(self) -> dict[Literal['function', 'filter'], dict[str, Callable[..., Any]]]:
		"""@see decl"""
		...


class Renderer:
	"""テンプレートレンダー"""

	def __init__(self, env_paths: DataEnvPath, setting: RendererSetting, helper_provider: RendererHelperProvider) -> None:
		"""インスタンスを生成

		Args:
			env_paths: 環境パス(データ用)
			setting: テンプレートレンダー設定データ
			helper_privider: ヘルパープロバイダー
		"""
		template_dirs = self.__make_template_dirs(env_paths, setting)
		self.__renderer = Environment(loader=FileSystemLoader(template_dirs, encoding='utf-8'), auto_reload=False)
		self.__apply_helpers(helper_provider)

	def __make_template_dirs(self, env_paths: DataEnvPath, setting: RendererSetting, ) -> list[str]:
		"""テンプレートの入力ディレクトリーリストを生成

		Args:
			env_paths: 環境パス(データ用)
			setting: テンプレートレンダー設定データ
		Returns:
			入力ディレクトリーリスト
		"""
		template_dirs: list[str] = []
		for env_path in env_paths:
			for template_dir in setting.template_dirs:
				in_template_dir = os.path.abspath(os.path.join(env_path, template_dir))
				if os.path.exists(in_template_dir):
					template_dirs.append(in_template_dir)

		return template_dirs

	def __apply_helpers(self, helper_provider: RendererHelperProvider) -> None:
		"""テンプレートヘルパーを適用

		Args:
			helper_privider: ヘルパープロバイダー
		"""
		for tag, helpers in helper_provider().items():
			for name, helper in helpers.items():
				if tag == 'function':
					self.__renderer.globals[name] = helper
				elif tag == 'filter':
					self.__renderer.filters[name] = helper

	def render(self, template: str, vars: dict[str, Any] = {}) -> str:
		"""テンプレートをレンダリング

		Args:
			template: テンプレートファイルの名前
			vars (dict[str, Any]) テンプレートへの入力変数(default = {})
		Returns:
			レンダリング結果
		"""
		return self.__renderer.get_template(f'{template}.j2').render(vars)
