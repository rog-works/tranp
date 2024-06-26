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


def parse_block(text: str, brakets: str = '()', groups: list[int] = []) -> list[str]:
	"""文字列内の括弧で囲われたブロックを展開する

	Args:
		text (str): 対象の文字列
		brakets (str): 括弧のペア (default: '()')
		groups (list[int]): レスポンス対象のインデックス。[]=無制限 (default: [])
	Returns:
		list[str]: 展開したブロックのリスト
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
	return [text[found[0]:found[1]] for index, found in enumerate(founds) if len(groups) == 0 or index in groups]


def parse_pair_block(text: str, brakets: str = '{}', delimiter: str = ':', groups: list[int] = []) -> list[list[str]]:
	"""文字列内のペアブロックを展開する。主に連想配列が対象

	Args:
		text (str): 対象の文字列
		brakets (str): 括弧のペア (default: '{}')
		delimiter (str): 区切り文字 (default: ':')
		groups (list[int]): レスポンス対象のインデックス。[]=無制限 (default: [])
	Returns:
		list[tuple[str, str]]: [[キー, 値], ...]
	"""
	chars = f'{brakets}{delimiter}'
	founds: list[tuple[int, list[str]]] = []
	stack: list[tuple[int, list[int]]] = []
	index = 0
	while index < len(text):
		if text[index] not in chars:
			index = index + 1
			continue

		if text[index] == brakets[0]:
			stack.append((index + 1, []))
		elif text[index] == delimiter:
			peek = stack.pop()
			peek[1].append(index)
			stack.append(peek)
		elif text[index] == brakets[1] and len(stack) > 0 and len(stack[-1][1]) > 0:
			start, splits = stack.pop()
			offsets = [*splits, index]
			curr = start
			in_texts: list[str] = []
			for offset in offsets:
				in_texts.append(text[curr:offset].lstrip())
				curr = offset + 1

			founds.append((start, in_texts))

		index = index + 1

	founds = sorted(founds, key=lambda entry: entry[0])
	return [found[1] for index, found in enumerate(founds) if len(groups) == 0 or index in groups]
