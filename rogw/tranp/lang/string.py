import re


def camelize(org: str) -> str:
	"""アッパーキャメルケースに変換
	
	Args:
		org: 元の文字列
	Returns:
		変換後の文字列
	"""
	return ''.join([elem.capitalize() for elem in org.split('_')])


def snakelize(org: str) -> str:
	"""スネークケースに変換
	
	Args:
		org: 元の文字列
	Returns:
		変換後の文字列
	"""
	return re.sub('^[_]+', '', re.sub('([A-Z])', r'_\1', org).lower())
