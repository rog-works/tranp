from typing import ClassVar


class Versions:
	"""バージョンを管理

	Attributes:
		app: アプリケーションのバージョン
		py2cpp: Py2Cppのバージョン
	"""

	app: ClassVar = '0.9.7'
	py2cpp: ClassVar = '0.9.0'
