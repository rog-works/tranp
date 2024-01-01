import json
import hashlib
import os
from typing import Any, Generic, IO, Protocol, TypeVar


class Lifecycle(Protocol):
	def instantiate(self) -> Any:
		...

	def context(self) -> dict[str, str]:
		...

	def save(self, instance: Any, f: IO) -> None:
		...

	def load(self, f: IO) -> Any:
		...


T = TypeVar('T', bound=Lifecycle)


class CachedProxy(Generic[T]):
	def __init__(self, lifecycle: T) -> None:
		self.__lifecycle = lifecycle

	def get(self, filepath: str) -> Any:
		cache_filepath = self.to_cache_filepath(filepath)
		if self.cache_exists(cache_filepath):
			return self.load_cache(cache_filepath)

		instance = self.load_actual()
		self.save_cache(instance, cache_filepath)
		return instance

	def to_cache_filepath(self, filepath: str) -> str:
		basepath, extention = os.path.splitext(filepath)
		data = json.dumps(self.__lifecycle.context())
		identifer = hashlib.md5(data.encode('utf-8')).hexdigest()
		return f'{basepath}.{identifer}{extention}'

	def cache_exists(self, cache_filepath: str) -> bool:
		return os.path.exists(cache_filepath)

	def save_cache(self, instance: T, filepath: str) -> None:
		dirpath = os.path.dirname(filepath)
		if not os.path.exists(dirpath):
			os.makedirs(dirpath)

		with open(filepath, mode='wb') as f:
			self.__lifecycle.save(instance, f)

	def load_cache(self, filepath: str) -> T:
		with open(filepath, mode='rb') as f:
			return self.__lifecycle.load(f)

	def mtime_actual(self, filepath: str) -> float:
		return os.path.getmtime(filepath)
	
	def load_actual(self) -> Any:
		return self.__lifecycle.instantiate()
