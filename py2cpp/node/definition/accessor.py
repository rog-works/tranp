import re


def to_access(name: str) -> str:
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
