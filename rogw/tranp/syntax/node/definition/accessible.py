import re
from typing import ClassVar


def to_accessor(name: str) -> str:
	"""名前からアクセス修飾子に変換

	Args:
		name (str): 名前
	Returns:
		str: アクセス修飾子
	"""
	if re.fullmatch(r'__.+__', name):
		return 'public'
	elif name.startswith('__'):
		return 'private'
	elif name.startswith('_'):
		return 'protected'
	else:
		return 'public'


class PythonClassOperations:
	"""クラスオペレーション定義"""

	constructor: ClassVar = '__init__'
	iterator: ClassVar = '__next__'
	iterable: ClassVar = '__iter__'

	def operation_by(self, operator: str) -> str:
		"""各種演算に対応するメソッドの名称を取得

		Args:
			operator (str): 演算子
		Returns:
			str: メソッド名
		"""
		return self.__operators[operator]

	__operators: ClassVar = {
		'or': '__or__',  # FIXME &&に対応する特殊メソッドはない
		'and': '__and__',  # FIXME 同上
		'==': '__eq__',
		'<': '__lt__',
		'>': '__gt__',
		'<=': '__le__',
		'>=': '__ge__',
		'<>': '__not__',
		'!=': '__not__',
		'in': '__contains__',
		'not.in': '__contains__',  # XXX 型推論的に同じなので代用
		'is': '__eq__',  # XXX 型推論的に同じなので代用
		'is.not': '__not__',  # XXX 型推論的に同じなので代用
		# Bitwise
		'|': '__or__',
		'^': '__xor__',
		'&': '__and__',
		'<<': '__lshift__',
		'>>': '__rshift__',
		# Arthmetic
		'+': '__add__',
		'-': '__sub__',
		'*': '__mul__',
		'/': '__truediv__',
		'%': '__mod__',
	}
