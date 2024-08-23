from rogw.tranp.semantics.reflection.base import IReflection
from rogw.tranp.semantics.reflection.interfaces import IConvertion, IFunction, IIterator, IObject


class Object(IReflection, IConvertion, IObject):
	"""リフレクション拡張(オブジェクト)"""


class Iterator(IReflection, IIterator):
	"""リフレクション拡張(イテレーター)"""


class Function(IReflection, IFunction):
	"""リフレクション拡張(ファンクション)"""
