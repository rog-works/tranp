from dataclasses import dataclass
import glob
import json
import hashlib
import os
import re
from typing import Any, Callable, Generic, IO, Protocol, TypeVar

from tranp.lang.implementation import implements


class Stored(Protocol):
	"""ストアインターフェイス"""

	@classmethod
	def load(cls, stream: IO) -> 'Stored':
		"""インスタンスを復元

		Args:
			stream (IO): IO
		Returns:
			Stored: 復元したインスタンス
		"""
		...

	def save(self, stream: IO) -> None:
		"""インスタンスを保存

		Args:
			stream (IO): IO
		"""
		...


T = TypeVar('T', bound=Stored)


class Cached(Generic[T]):
	"""キャッシュの抽象基底クラス"""

	@classmethod
	def identifier(cls, identity: dict[str, str]) -> str:
		"""一意性担保用のコンテキストから一意な識別子を生成

		Args:
			identity (dict[str, str]): 一意性担保用のコンテキスト
		Returns:
			str: 一意な識別子
		"""
		data = json.dumps(identity)
		return hashlib.md5(data.encode('utf-8')).hexdigest()

	def __init__(self, stored: T, factory: Callable[[], T], identity: dict[str, str], basedir: str, **options: Any) -> None:
		"""インスタンスを生成

		Args:
			stored (T): ストアインターフェイス
			factory (Callable[[], T]): ファクトリー
			identity (dict[str, str]): 一意性担保用のコンテキスト
			basedir (str): キャッシュの保存ディレクトリー(実行ディレクトリーからの相対パス)
			**options (Any): オプション
		"""
		self._stored = stored
		self._factory = factory
		self._identity = identity
		self._basedir = basedir
		self._options = options

	def get(self, cache_key: str) -> T:
		"""インスタンスの取得プロクシー

		Args:
			cache_key (str): キャッシュキー
		Returns:
			T: インスタンス
		"""
		raise NotImplementedError()


class CachedProxy(Cached[T]):
	"""キャッシュ実装。キャッシュを優先してインスタンスを取得するプロクシー

	Note:
		キャッシュの保存先はcache_keyとidentityによって一意性を担保したパスに変換する
		### 例
		cache_key: 'path/to/cache'
		identity: {'mtime': str(os.path.getmtime('path/to/actual'))}
		'${cache_key}-${md5(json.dumps(identity))}' -> 'path/to/cache-12345678901234567890123456789012'
	"""

	@implements
	def get(self, cache_key: str) -> T:
		"""インスタンスの取得プロクシー

		Args:
			cache_key (str): キャッシュキー
		Returns:
			T: インスタンス
		"""
		cache_path = self.to_cache_path(cache_key)
		if self.cache_exists(cache_path):
			return self.load_cache(cache_path)

		instance = self.instantiate()
		self.save_cache(instance, cache_path)
		return instance

	def to_cache_path(self, cache_key: str) -> str:
		"""キャッシュファイルパスに変換

		Args:
			cache_key (str): キャッシュキー
		Returns:
			str: キャッシュファイルパス
		Note:
			ファイルパスに一意性を担保する文字列を付与する
		"""
		basepath = os.path.join(self._basedir, cache_key)
		file_format = self._options.get('format', '')
		extention = f'.{file_format}' if file_format else ''
		return f'{basepath}-{self.identifier(self._identity)}{extention}'

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
			instance.save(f)

	def find_oldest(self, cache_path: str) -> list[str]:
		"""旧キャッシュファイルを検索

		Args:
			cache_path (str): キャッシュファイルパス(実行ディレクトリーからの相対パス)
		Returns:
			list[str]: 旧キャッシュファイルパスリスト
		"""
		# FIXME 拡張子が無いと検索できない
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
			return self._stored.load(f)
	
	def instantiate(self) -> T:
		"""インスタンスを生成

		Returns:
			T: インスタンス
		"""
		return self._factory()


class CachedDummy(Cached[T]):
	"""キャッシュダミー。このクラスはキャッシュを無効にする以外の機能はない"""

	@implements
	def get(self, cache_key: str) -> T:
		"""インスタンスの取得プロクシー

		Args:
			cache_key (str): キャッシュキー
		Returns:
			T: インスタンス
		"""
		return self._factory()


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
		self.__instances: dict[str, Any] = {}

	def get(self, cache_key: str, identity: dict[str, str] = {}, **options: Any) -> Callable[[Callable[[], T]], Callable[[], T]]:
		"""キャッシュデコレーター。ファクトリー関数をラップしてキャッシュ機能を付与

		Args:
			cache_key (str): キャッシュキー
			identity (dict[str, str]): 一意性担保用のコンテキスト
			**options (Any): オプション
		Returns:
			Callable: デコレーター
		Examples:
			```python
			class Data:
				@classmethod
				def load(self, stream: IO) -> 'Data':
					...

				def save(self, strem: IO) -> None:
					...

			def loader(path: str) -> Data:
				cache = CacheProvider(setting)

				@cache.get('data.cache', identity={'mtime': str(os.path.getmtime(path))})
				def wrap_factory() -> Data:
					return Data.very_slow_factory(path)

				return wrap_factory()
			```
		"""
		def decorator(wrapped: Callable[[], T]) -> Callable[[], T]:
			def wrapper() -> T:
				stored = wrapped.__annotations__['return']
				ctor = CachedProxy if self.__setting.enabled else CachedDummy
				identifier = ctor.identifier({'__cache_key__': cache_key, **identity})
				if identifier not in self.__instances:
					cacher = ctor(stored, wrapped, identity, self.__setting.basedir, **options)
					self.__instances[identifier] = cacher.get(cache_key)

				return self.__instances[identifier]

			return wrapper
		return decorator
