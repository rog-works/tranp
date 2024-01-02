from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
import glob
import json
import hashlib
import os
import re
from typing import Generic, IO, TypeVar

from py2cpp.lang.annotation import implements

T = TypeVar('T')


class Lifecycle(Generic[T], metaclass=ABCMeta):
	"""インスタンスのライフサイクルイベントを扱うインターフェイス"""

	@abstractmethod
	def instantiate(self) -> T:
		"""インスタンスを生成

		Returns:
			T: 生成したインスタンス
		"""
		raise NotImplementedError()

	@abstractmethod
	def context(self) -> dict[str, str]:
		"""インスタンスの一意性を担保するコンテキストを生成

		Returns:
			dict[str, str]: コンテキスト
		"""
		raise NotImplementedError()

	@abstractmethod
	def save(self, instance: T, f: IO) -> None:
		"""インスタンスを保存

		Args:
			instance (T): 対象のインタスタンス
			f (IO): ファイルオブジェクト
		"""
		raise NotImplementedError()

	@abstractmethod
	def load(self, f: IO) -> T:
		"""インスタンスを読み込み

		Args:
			f (IO): ファイルオブジェクト
		Returns:
			T: ロードしたインスタンス
		"""
		raise NotImplementedError()


class Cached(Generic[T]):
	"""キャッシュの抽象基底クラス"""

	def __init__(self, lifecycle: Lifecycle[T], basedir: str) -> None:
		"""インスタンスを生成

		Args:
			lifecycle (Lifecycle[T]): ライフサイクル
			basedir (str): キャッシュの保存ディレクトリー(実行ディレクトリーからの相対パス)
		"""
		self._lifecycle = lifecycle
		self._basedir = basedir

	def get(self, filepath: str) -> T:
		"""インスタンスの取得プロクシー

		Args:
			filepath (str): ファイルパス(保存ディレクトリーからの相対パス)
		Returns:
			T: インスタンス
		"""
		raise NotImplementedError()


class CachedProxy(Cached[T]):
	"""キャッシュ実装。キャッシュを優先してインスタンスを取得するプロクシー

	Note:
		キャッシュの保存先はgetの引数であるfilepathを元にLifecycle.contextによって一意性を担保したパスに変換する
		例) filepath: 'path/to/data.json' -> 'path/to/data-12345678901234567890123456789012.json'
	"""

	@implements
	def get(self, filepath: str) -> T:
		"""インスタンスの取得プロクシー

		Args:
			filepath (str): ファイルパス(保存ディレクトリーからの相対パス)
		Returns:
			T: インスタンス
		"""
		cache_path = self.to_cache_path(filepath)
		if self.cache_exists(cache_path):
			return self.load_cache(cache_path)

		instance = self.instantiate()
		self.save_cache(instance, cache_path)
		return instance

	def to_cache_path(self, filepath: str) -> str:
		"""キャッシュファイルパスに変換

		Args:
			filepath (str): ファイルパス(保存ディレクトリーからの相対パス)
		Returns:
			str: キャッシュファイルパス
		Note:
			ファイルパスに一意性を担保する文字列を付与する
		"""
		relpath, extention = os.path.splitext(filepath)
		basepath = os.path.join(self._basedir, relpath)
		data = json.dumps(self._lifecycle.context())
		identifer = hashlib.md5(data.encode('utf-8')).hexdigest()
		return f'{basepath}-{identifer}{extention}'

	def cache_exists(self, cache_path: str) -> bool:
		"""キャッシュファイルが存在するか判定

		Args:
			cache_path (str): キャッシュファイルパス(実行ディレクトリーからの相対パス)
		Returns:
			bool: True = 存在
		"""
		return os.path.exists(cache_path)

	def save_cache(self, instance: T, cache_path: str) -> None:
		"""インスタンスをファイルに保存

		Args:
			instance (T): インスタンス
			cache_path (str): キャッシュファイルパス(実行ディレクトリーからの相対パス)
		Note:
			保存直前に古いキャッシュファイルを自動的に削除
		"""
		dirpath = os.path.dirname(cache_path)
		if not os.path.exists(dirpath):
			os.makedirs(dirpath)

		for oldedst in self.find_oldest(cache_path):
			os.unlink(oldedst)

		with open(cache_path, mode='wb') as f:
			self._lifecycle.save(instance, f)

	def find_oldest(self, cache_path: str) -> list[str]:
		"""旧キャッシュファイルを検索

		Args:
			cache_path (str): キャッシュファイルパス(実行ディレクトリーからの相対パス)
		Returns:
			list[str]: 旧キャッシュファイルパスリスト
		"""
		glob_pattern = re.sub(r'-(\w{32})(\.\w+$)', r'-*\2', cache_path)
		return glob.glob(glob_pattern)

	def load_cache(self, cache_path: str) -> T:
		"""インスタンスをファイルから読み込み

		Args:
			cache_path (str): キャッシュファイルパス(実行ディレクトリーからの相対パス)
		Returns:
			T: 読み込んだインスタンス
		"""
		with open(cache_path, mode='rb') as f:
			return self._lifecycle.load(f)
	
	def instantiate(self) -> T:
		"""インスタンスを生成

		Returns:
			T: インスタンス
		"""
		return self._lifecycle.instantiate()


class CachedDummy(Cached[T]):
	"""キャッシュダミー。このクラスはキャッシュを無効にする以外の機能はない"""

	@implements
	def get(self, filepath: str) -> T:
		"""インスタンスの取得プロクシー

		Args:
			filepath (str): ファイルパス(保存ディレクトリーからの相対パス)
		Returns:
			T: インスタンス
		"""
		return self._lifecycle.instantiate()


@dataclass
class CacheSetting:
	"""キャッシュ設定データ

	Attributes:
		basedir (str): キャッシュの保存ディレクトリー(実行ディレクトリーからの相対パス)
		enabled (bool): True = 有効(default = True)
	"""

	basedir: str
	enabled: bool = True


class CacheProvider:
	"""キャッシュプロバイダー"""

	def __init__(self, setting: CacheSetting) -> None:
		"""インスタンスを生成

		Args:
			setting (CacheSetting): キャッシュ設定データ
		"""
		self.__setting = setting

	def provide(self, lifecycle: Lifecycle[T]) -> Cached[T]:
		"""キャッシュプロクシーを生成

		Args:
			lifecycle (Lifecycle[T]): ライフサイクル
		Returns:
			Cached[T]: キャッシュプロクシー
		"""
		if self.__setting.enabled:
			return CachedProxy[T](lifecycle, self.__setting.basedir)
		else:
			return CachedDummy[T](lifecycle, self.__setting.basedir)
