from rogw.tranp.semantics.reflection.extensions import IFunction, IObject
from rogw.tranp.semantics.reflection.interface import IReflection


class Class(IReflection, IObject):
	"""リフレクション拡張(クラス)"""


class Function(IReflection, IFunction):
	"""リフレクション拡張(ファンクション)"""
