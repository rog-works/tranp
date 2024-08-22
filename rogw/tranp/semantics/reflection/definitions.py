from rogw.tranp.semantics.reflection.base import IReflection
from rogw.tranp.semantics.reflection.interfaces import IFunction, IObject


class Class(IReflection, IObject):
	"""リフレクション拡張(クラス)"""


class Function(IReflection, IFunction):
	"""リフレクション拡張(ファンクション)"""
