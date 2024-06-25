import re


def camelize(org: str) -> str:
	"""アッパーキャメルケースに変換
	
	Args:
		org (str): 元の文字列
	Returns:
		str: 変換後の文字列
	"""
	return ''.join([elem.capitalize() for elem in org.split('_')])


def snakelize(org: str) -> str:
	"""スネークケースに変換
	
	Args:
		org (str): 元の文字列
	Returns:
		str: 変換後の文字列
	"""
	return re.sub('^[_]+', '', re.sub('([A-Z])', r'_\1', org).lower())


def parse_brakets(text: str, brakets: str = '()', limit: int = -1) -> list[str]:
	"""文字列内の括弧のペアを展開する

	Args:
		text (str): 対象の文字列
		brakets (str): 括弧のペア (default: '()')
		limit (int): 展開上限。-1=無制限 (default: -1)
	"""
	founds: list[tuple[int, int]] = []
	stack: list[int] = []
	index = 0
	while index < len(text):
		if text[index] in brakets:
			if text[index] == brakets[0]:
				stack.append(index)
			else:
				start = stack.pop()
				founds.append((start, index + 1))

		index = index + 1

	founds = sorted(founds, key=lambda entry: entry[0])
	return [text[found[0]:found[1]] for index, found in enumerate(founds) if limit == -1 or index < limit]
