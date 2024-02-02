from py2cpp.analyze.processor import Preprocessors
import py2cpp.analyze.processors as procs


def preprocessors() -> Preprocessors:
	"""プリプロセッサープロバイダーを生成
	
	Returns:
		Preprocessors: プリプロセッサープロバイダー
	"""
	return lambda: [
		procs.FromModules(),
		procs.ResolveGeneric(),
		procs.ResolveUnknown(),
		procs.RuntimeRegister(),
	]
