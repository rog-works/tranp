from py2cpp.analize.processor import Preprocessors
import py2cpp.analize.processors.from_modules as procs


def preprocessors() -> Preprocessors:
	"""プロセッサープロバイダーを生成
	
	Returns:
		Preprocessors: プロセッサープロバイダー
	"""
	return lambda: [
		procs.FromModules(),
	]
