import json
import os

from rogw.tranp.io.cache import CacheSetting
from rogw.tranp.io.loader import IFileLoader
from rogw.tranp.lang.annotation import implements, injectable
from rogw.tranp.lang.module import module_path_to_filepath
from rogw.tranp.module.module import Module
from rogw.tranp.semantics.reflection.db import SymbolDB
from rogw.tranp.semantics.reflection.serialization import IReflectionSerializer


class ISymbolDBPersistor:
	"""シンボルテーブル永続化インターフェイス"""

	def stored(self, module: Module) -> bool:
		"""シンボルテーブルが永続化されているか判定

		Args:
			module (Module): モジュール
		Returns:
			bool: True = 永続化
		"""
		...

	def store(self, module: Module, db: SymbolDB) -> None:
		"""シンボルテーブルを永続化

		Args:
			module (Module): モジュール
			db (SymbolDB): シンボルテーブル
		"""
		...

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
	def __init__(self, setting: CacheSetting, serializer: IReflectionSerializer, files: IFileLoader) -> None:
		"""インスタンスを生成

		Args:
			setting (CacheSetting): キャッシュ設定 @inject
			serializer (IReflectionSerializer): シンボルシリアライザー @inject
			files (IFileLoader) ファイルローダー @inject
		"""
		self.setting = setting
		self.serializer = serializer
		self.files = files

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
		"""ファイルパスを生成

		Args:
			module (Module): モジュール
		Returns:
			str: ファイルパス
		"""
		basepath = module_path_to_filepath(module.path)
		identity = module.identity()
		return f'{os.path.join(self.setting.basedir, f'{basepath}-symbols-{identity}')}.json'

	def _can_store(self, module: Module, filepath: str) -> bool:
		"""保存を実施するか判定

		Args:
			module (Module): モジュール
			filepath (str): ファイルパス
		Returns:
			bool: True = 実施
		"""
		return module.in_storage() and not self.files.exists(filepath)

	def _can_restore(self, module: Module, filepath: str) -> bool:
		"""復元を実施するか判定

		Args:
			module (Module): モジュール
			filepath (str): ファイルパス
		Returns:
			bool: True = 実施
		"""
		return self.setting.enabled and module.in_storage() and self.files.exists(filepath)

	def _store(self, module: Module, db: SymbolDB, filepath: str) -> None:
		"""ストレージに保存

		Args:
			module (Module): モジュール
			db (SymbolDB): シンボルテーブル
			filepath (str): ファイルパス
		"""
		# FIXME FileLoaderの解決するパスと食い違いが生まれるため修正を検討
		data = db.to_json(self.serializer, module_path=module.path)
		with open(filepath, mode='wb') as f:
			json_str = json.dumps(data, separators=(',', ':'))
			f.write(json_str.encode('utf-8'))

	def _restore(self, db: SymbolDB, filepath: str) -> None:
		"""ストレージから復元

		Args:
			db (SymbolDB): シンボルテーブル
			filepath (str): ファイルパス
		"""
		content = self.files.load(filepath)
		data = json.loads(content)
		db.load_json(self.serializer, data)
