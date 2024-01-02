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
	@abstractmethod
	def instantiate(self) -> T:
		raise NotImplementedError()

	@abstractmethod
	def context(self) -> dict[str, str]:
		raise NotImplementedError()

	@abstractmethod
	def save(self, instance: T, f: IO) -> None:
		raise NotImplementedError()

	@abstractmethod
	def load(self, f: IO) -> T:
		raise NotImplementedError()


class Cached(Generic[T]):
	def __init__(self, lifecycle: Lifecycle[T], basedir: str) -> None:
		self._lifecycle = lifecycle
		self._basedir = basedir

	def get(self, filepath: str) -> T:
		...


class CachedProxy(Cached[T]):
	@implements
	def get(self, filepath: str) -> T:
		cache_filepath = self.to_cache_filepath(filepath)
		if self.cache_exists(cache_filepath):
			return self.load_cache(cache_filepath)

		instance = self.load_actual()
		self.save_cache(instance, cache_filepath)
		return instance

	def to_cache_filepath(self, filepath: str) -> str:
		relpath, extention = os.path.splitext(filepath)
		basepath = os.path.join(self._basedir, relpath)
		data = json.dumps(self._lifecycle.context())
		identifer = hashlib.md5(data.encode('utf-8')).hexdigest()
		return f'{basepath}-{identifer}{extention}'

	def cache_exists(self, cache_filepath: str) -> bool:
		return os.path.exists(cache_filepath)

	def save_cache(self, instance: T, filepath: str) -> None:
		dirpath = os.path.dirname(filepath)
		if not os.path.exists(dirpath):
			os.makedirs(dirpath)

		for oldedst in self.find_oldest(filepath):
			os.unlink(oldedst)

		with open(filepath, mode='wb') as f:
			self._lifecycle.save(instance, f)

	def find_oldest(self, new_filepath: str) -> list[str]:
		glob_pattern = re.sub(r'-(\w{32})(\.\w+$)', r'-*\2', new_filepath)
		return glob.glob(glob_pattern)

	def load_cache(self, filepath: str) -> T:
		with open(filepath, mode='rb') as f:
			return self._lifecycle.load(f)

	def mtime_actual(self, filepath: str) -> float:
		return os.path.getmtime(filepath)
	
	def load_actual(self) -> T:
		return self._lifecycle.instantiate()


class CachedDummy(Cached[T]):
	@implements
	def get(self, filepath: str) -> T:
		return self._lifecycle.instantiate()


@dataclass
class CacheSetting:
	basedir: str
	enabled: bool = True


class CacheProvider:
	def __init__(self, setting: CacheSetting) -> None:
		self.__setting = setting

	def provide(self, lifecycle: Lifecycle[T]) -> Cached[T]:
		if self.__setting.enabled:
			return CachedProxy[T](lifecycle, self.__setting.basedir)
		else:
			return CachedDummy[T](lifecycle, self.__setting.basedir)
