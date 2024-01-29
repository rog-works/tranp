import re


def to_access(name: str) -> str:
	if re.fullmatch(r'__.+__', name):
		return 'public'
	elif name.startswith('__'):
		return 'private'
	elif name.startswith('_'):
		return 'protected'
	else:
		return 'public'
