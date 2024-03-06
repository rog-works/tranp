from typing import ClassVar, Protocol


class IVersion(Protocol):
	"""バージョン管理プロトコル"""

	@property
	def version(self) -> str:
		"""str: バージョン"""
		...


class Versions:
	"""バージョンを管理

	Attributes:
		app (str): アプリケーションのバージョン
		py2cpp (str): Py2Cppのバージョン
	"""
	app: ClassVar = '1.0.0'
	py2cpp: ClassVar = '1.0.0'
