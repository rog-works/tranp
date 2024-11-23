from abc import ABCMeta, abstractmethod
import glob
import json
import os

from rogw.tranp.cache.cache import CacheSetting
from rogw.tranp.file.loader import ISourceLoader
from rogw.tranp.lang.annotation import implements, injectable
from rogw.tranp.lang.module import module_path_to_filepath
from rogw.tranp.module.module import Module
from rogw.tranp.semantics.reflection.db import SymbolDB
from rogw.tranp.semantics.reflection.serialization import IReflectionSerializer


class ISymbolDBPersistor(metaclass=ABCMeta):
	"""シンボルテーブル永続化インターフェイス"""

	@abstractmethod
	def stored(self, module: Module) -> bool:
		"""シンボルテーブルが永続化されているか判定

		Args:
			module (Module): モジュール
		Returns:
			bool: True = 永続化
		"""
		...

	@abstractmethod
	def store(self, module: Module, db: SymbolDB) -> None:
		"""シンボルテーブルを永続化

		Args:
			module (Module): モジュール
			db (SymbolDB): シンボルテーブル
		"""
		...

	@abstractmethod
	def restore(self, module: Module, db: SymbolDB) -> None:
		"""シンボルテーブルを復元

		Args:
			module (Module): モジュール
			db (SymbolDB): シンボルテーブル
		"""
		...


class SymbolDBPersistor(ISymbolDBPersistor):
	"""シンボルテーブル永続化"""

	@injectable
	def __init__(self, setting: CacheSetting, serializer: IReflectionSerializer, sources: ISourceLoader) -> None:
		"""インスタンスを生成

		Args:
			setting (CacheSetting): キャッシュ設定 @inject
			serializer (IReflectionSerializer): シンボルシリアライザー @inject
			sources (ISourceLoader) ソースコードローダー @inject
		"""
		self.setting = setting
		self.serializer = serializer
		self.sources = sources

	@implements
	def stored(self, module: Module) -> bool:
		"""シンボルテーブルが永続化されているか判定

		Args:
			module (Module): モジュール
		Returns:
			bool: True = 永続化
		"""
		return self._can_restore(module, self._gen_filepath(module))

	@implements
	def store(self, module: Module, db: SymbolDB) -> None:
		"""シンボルテーブルを永続化

		Args:
			module (Module): モジュール
			db (SymbolDB): シンボルテーブル
		"""
		filepath = self._gen_filepath(module)
		if self._can_store(module, filepath):
			self._store(module, db, filepath)

	@implements
	def restore(self, module: Module, db: SymbolDB) -> None:
		"""シンボルテーブルを復元

		Args:
			module (Module): モジュール
			db (SymbolDB): シンボルテーブル
		"""
		filepath = self._gen_filepath(module)
		if self._can_restore(module, filepath):
			self._restore(db, filepath)

	def _gen_filepath(self, module: Module) -> str:
		"""保存ファイルの絶対パスを生成

		Args:
			module (Module): モジュール
		Returns:
			str: 絶対パス
		"""
		basepath = module_path_to_filepath(module.path)
		identity = module.identity()
		filename = f'{basepath}-symbols-{identity}.json'
		return os.path.abspath(os.path.join(os.getcwd(), self.setting.basedir, filename))

	def _gen_glob_pattern(self, module: Module) -> str:
		"""旧ファイル検索用のGlobパターンを生成

		Args:
			module (Module): モジュール
		Returns:
			str: Globパターン
		"""
		basepath = module_path_to_filepath(module.path)
		filename = f'{basepath}-symbols-*.json'
		return os.path.abspath(os.path.join(os.getcwd(), self.setting.basedir, filename))

	def _can_store(self, module: Module, filepath: str) -> bool:
		"""保存を実施するか判定

		Args:
			module (Module): モジュール
			filepath (str): ファイルパス
		Returns:
			bool: True = 実施
		"""
		return module.in_storage() and not self.sources.exists(filepath)

	def _can_restore(self, module: Module, filepath: str) -> bool:
		"""復元を実施するか判定

		Args:
			module (Module): モジュール
			filepath (str): ファイルパス
		Returns:
			bool: True = 実施
		"""
		return self.setting.enabled and module.in_storage() and self.sources.exists(filepath)

	def _store(self, module: Module, db: SymbolDB, filepath: str) -> None:
		"""ストレージに保存

		Args:
			module (Module): モジュール
			db (SymbolDB): シンボルテーブル
			filepath (str): ファイルパス
		"""
		for oldest in self._find_oldest(module):
			os.unlink(oldest)

		data = db.to_json(self.serializer, for_module_path=module.path)
		with open(filepath, mode='wb') as f:
			json_str = json.dumps(data, separators=(',', ':'))
			f.write(json_str.encode('utf-8'))

	def _restore(self, db: SymbolDB, filepath: str) -> None:
		"""ストレージから復元

		Args:
			db (SymbolDB): シンボルテーブル
			filepath (str): ファイルパス
		"""
		content = self.sources.load(filepath)
		data = json.loads(content)
		db.import_json(self.serializer, data)

	def _find_oldest(self, module: Module) -> list[str]:
		"""旧ファイルを検索

		Args:
			module (Module): モジュール
		Returns:
			list[str]: 旧ファイルのパスリスト
		"""
		return glob.glob(self._gen_glob_pattern(module))
