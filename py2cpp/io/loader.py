import os

from py2cpp.app.env import Env


class FileLoader:
	def __init__(self, env: Env) -> None:
		self.__env = env

	def load(self, filepath: str) -> str:
		found_filepath = self.__resolve_filepath(filepath)
		if found_filepath is None:
			raise FileNotFoundError(f'No such file or directory. filepath: {filepath}')

		with open(found_filepath, mode='r', encoding='utf-8') as f:
			return '\n'.join(f.readlines())

	def mtime(self, filepath: str) -> float:
		found_filepath = self.__resolve_filepath(filepath)
		if found_filepath is None:
			raise FileNotFoundError(f'No such file or directory. filepath: {filepath}')

		return os.path.getmtime(found_filepath)

	def __resolve_filepath(self, filepath: str) -> str | None:
		for path in self.__env.paths:
			abs_filepath = os.path.abspath(os.path.join(path, filepath))
			if os.path.isfile(abs_filepath):
				return abs_filepath

		return None
