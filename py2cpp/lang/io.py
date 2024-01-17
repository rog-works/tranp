import os

from py2cpp.lang.env import Env


class FileLoader:
	def __init__(self, env: Env) -> None:
		self.__env = env

	def __call__(self, filepath: str) -> str:
		for path in self.__env.paths:
			abs_filepath = os.path.abspath(os.path.join(path, filepath))
			if not os.path.isfile(abs_filepath):
				continue

			with open(abs_filepath, mode='r', encoding='utf-8') as f:
				return '\n'.join(f.readlines())

		raise FileNotFoundError(f'No such file or directory. filepath: {filepath}')
