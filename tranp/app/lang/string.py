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


def is_quoted_literal(string: str, quote: str) -> bool:
	"""引用符に囲われた文字列リテラルか否か判定

	Args:
		string: 文字列
		quote: 引用符
	Returns:
		True = 文字列リテラル
	"""
	if not (string.startswith(quote) and string.endswith(quote)):
		return False

	index = 1
	length = len(string)
	while index < length - 1:
		found = string.find(quote, index, length - 1)
		if found == -1:
			break
		elif string[found - 1] != '\\':
			return False

		index = found + 1

	return True
