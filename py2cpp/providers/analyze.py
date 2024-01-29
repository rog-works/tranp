from py2cpp.analize.processor import Preprocessors
import py2cpp.analize.processors.from_modules as procs


def preprocessors() -> Preprocessors:
	"""プリプロセッサープロバイダーを生成
	
	Returns:
		Preprocessors: プリプロセッサープロバイダー
	"""
	return lambda: [
		procs.FromModules(),
	]
