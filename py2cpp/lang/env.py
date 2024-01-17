import os
from typing import Any

from py2cpp.lang.dict import deep_merge


class Env:
	def __init__(self, env: dict[str, Any]) -> None:
		self.__env = deep_merge(self.__default_env(), env)

	def __default_env(self) -> dict[str, Any]:
		paths = [
			os.getcwd(),
			os.path.join(os.getcwd(), 'py2cpp/compatible/python'),
		]
		return {'PYTHONPATH': {path: path for path in paths}}

	@property
	def paths(self) -> list[str]:
			return self.__env['PYTHONPATH'].values()
