import hashlib
import json
import os
from typing import Any

from rogw.tranp.errors import LogicError
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.annotation import injectable
from rogw.tranp.lang.locator import Locator
from rogw.tranp.module.types import ModulePath
from rogw.tranp.syntax.ast.dsn import DSN
from rogw.tranp.translator.types import ITranslator
from rogw.tranp.version import Versions


class AppMeta:
	"""アプリケーションのメタ情報"""

	def __init__(self, version: str, origin: dict[str, str], translator: dict[str, str]) -> None:
		"""インスタンスを生成
		
		Args:
			version (str): アプリケーションのバージョン
			origin (dict[str, str]): 翻訳元のソースコードのメタ情報
			translator (dict[str, str]): トランスレーターのメタ情報
		"""
		self.version = version
		self.origin = origin
		self.translator = translator

	@property
	def identity(self) -> str:
		"""str: 一意な識別子"""
		return hashlib.md5(self.to_json().encode('utf-8')).hexdigest()

	def __eq__(self, other: Any) -> bool:
		"""比較演算子のおバーロード
		
		Args:
			other (Any): 比較対象
		Returns:
			bool: True = 一致
		Raises:
			LogicError: 同種以外のインスタンスを指定
		"""
		if type(other) is not AppMeta:
			raise LogicError(f'Not allowed comparison. other: {type(other)}')

		return self.identity == other.identity

	def to_json(self) -> str:
		"""JSONにシリアライズ

		Returns:
			str: JSON文字列
		"""
		return json.dumps({'version': self.version, 'origin': self.origin, 'translator': self.translator}, separators=(',', ':'))

	def to_header(self) -> str:
		"""ヘッダーに変換

		Returns:
			str: メタヘッダー
		"""
		return f'@tranp.meta: {self.to_json()}'


class AppMetaProvider:
	"""メタ情報プロバイダー

	Note:
		FIXME 依存関係が悪い、効率悪い、とにかく扱いにくいので改善を検討
		FIXME * Versions.appに依存するとトランスレーターに委譲できない
		FIXME * トランスレーターから欲しい情報は全て静的な情報でインスタンスは必要ない
		FIXME * 同じファイルをストレージから何度もロードするため効率が悪い
	"""

	@injectable
	def __init__(self, locator: Locator) -> None:
		"""インスタンスを生成

		Args:
			locator (Locator): ロケーター
		"""
		self.__locator = locator

	@property
	def __translator(self) -> ITranslator:
		"""ITranslator: トランスレーター"""
		return self.__locator.resolve(ITranslator)

	@property
	def __loader(self) -> IFileLoader:
		"""IFileLoader: ファイルローダー"""
		return self.__locator.resolve(IFileLoader)

	def can_update(self, module_path: ModulePath, to_language: str, new_meta: AppMeta) -> bool:
		"""翻訳後のソースと比較して更新可否を判定

		Args:
			module_path (ModulePath): モジュールパス
			to_language (str): 翻訳後の言語タグ
			new_meta (AppMeta): 新規のメタ情報
		Returns:
			bool: True = 更新
		"""
		if self.previews_exists(module_path, to_language):
			if new_meta == self.previews(module_path, to_language):
				return False

		return True

	def previews_exists(self, module_path: ModulePath, to_language: str) -> bool:
		"""翻訳後のソースが存在するか判定

		Args:
			module_path (ModulePath): モジュールパス
			to_language (str): 翻訳後の言語タグ
		Returns:
			bool: True = 存在
		"""
		filepath = self.__to_previews_filepath(module_path, to_language)
		return os.path.exists(filepath)

	def previews(self, module_path: ModulePath, to_language: str) -> AppMeta:
		"""翻訳後のソースからメタ情報を生成

		Args:
			module_path (ModulePath): モジュールパス
			to_language (str): 翻訳後の言語タグ
		Returns:
			AppMeta: メタ情報
		"""
		previews = self.__load_previews(module_path, to_language)
		return AppMeta(previews['version'], previews['origin'], previews['translator'])

	def new(self, module_path: ModulePath) -> AppMeta:
		"""翻訳後のメタ情報を新規で生成

		Args:
			module_path (ModulePath): モジュールパス
		Returns:
			AppMeta: メタ情報
		"""
		return AppMeta(Versions.app, self.__origin_meta(module_path), self.__translator_meta())

	def __to_previews_filepath(self, module_path: ModulePath, to_language: str) -> str:
		"""翻訳後のソースのファイルパスに変換

		Args:
			module_path (ModulePath): モジュールパス
			to_language (str): 翻訳後の言語タグ
		Returns:
			str: ファイルパス
		"""
		return DSN.join(module_path.path.replace('.', '/'), to_language)
	
	def __load_previews(self, module_path: ModulePath, to_language: str) -> dict[str, Any]:
		"""翻訳後のソースからメタ情報を生成(JSON)

		Args:
			module_path (ModulePath): モジュールパス
			to_language (str): 翻訳後の言語タグ
		Returns:
			dict[str, Any]: メタ情報
		"""
		filepath = self.__to_previews_filepath(module_path, to_language)
		source = self.__loader.load(filepath)
		header = source.split('\n')[0]
		meta_json_str = header.split('@tranp.meta: ')[1]
		return json.loads(meta_json_str)

	def __origin_meta(self, module_path: ModulePath) -> dict[str, str]:
		"""翻訳元のメタ情報を生成

		Args:
			module_path (ModulePath): モジュールパス
		Returns:
			dict[str, str]: メタ情報
		"""
		filepath = DSN.join(module_path.path.replace('.', '/'), module_path.language)
		source = self.__loader.load(filepath)
		return {
			'filepath': filepath,
			'hash': hashlib.md5(source.encode('utf-8')).hexdigest(),
		}

	def __translator_meta(self) -> dict[str, str]:
		"""トランスレーターのメタ情報を生成

		Returns:
			dict[str, str]: メタ情報
		"""
		return {
			'module': DSN.join(self.__translator.__module__, self.__translator.__class__.__name__),
			'version': self.__translator.version,
		}
