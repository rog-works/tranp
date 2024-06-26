import re
from typing import TypedDict


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


def parse_braket_block(text: str, brakets: str = '()') -> list[str]:
	"""文字列内の括弧で囲われたブロックを展開する

	Args:
		text (str): 対象の文字列
		brakets (str): 括弧のペア (default: '()')
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
	return [text[found[0]:found[1]] for found in founds]


BlockEntry = TypedDict('BlockEntry', {'name': str, 'elems': list[str]})


def parse_block(text: str, brakets: str = '{}', delimiter: str = ':') -> list[BlockEntry]:
	"""文字列内のブロックを展開する。対象: 連想配列, 関数コール

	Args:
		text (str): 対象の文字列
		brakets (str): 括弧のペア (default: '{}')
		delimiter (str): 区切り文字 (default: ':')
	Returns:
		list[BlockEntry]: [{'name': キー, 'elems': 値}, ...]
	"""
	chars = f'{brakets}{delimiter}'
	founds: list[tuple[int, str, list[str]]] = []
	stack: list[tuple[int, str, list[int]]] = []
	index = 0
	name = ''
	while index < len(text):
		if text[index] not in chars:
			# 空白以外を名前の構成要素とする
			if text[index] not in ' \n\t':
				name = name + text[index]
			else:
				name = ''

			index = index + 1
			continue

		if text[index] == brakets[0]:
			stack.append((index + 1, name, []))
			name = ''
		elif text[index] == delimiter:
			start, at_name, splits = stack.pop()
			splits.append(index)
			stack.append((start, at_name, splits))
		elif text[index] == brakets[1] and len(stack) > 0:
			start, at_name, splits = stack.pop()
			offsets = [*splits, index]
			curr = start
			in_texts: list[str] = []
			for offset in offsets:
				in_texts.append(text[curr:offset].lstrip())
				curr = offset + 1

			founds.append((start, at_name, in_texts))

		index = index + 1

	founds = sorted(founds, key=lambda entry: entry[0])
	return [{'name': found[1], 'elems': found[2]} for found in founds]


def parse_pair_block(text: str, brakets: str = '{}', delimiter: str = ':') -> list[tuple[str, str]]:
	"""文字列内のペアブロックを展開する。主に連想配列が対象

	Args:
		text (str): 対象の文字列
		brakets (str): 括弧のペア (default: '{}')
		delimiter (str): 区切り文字 (default: ':')
	Returns:
		list[tuple[str, str]]: [(キー, 値), ...]
	"""
	return [(entry['elems'][0], entry['elems'][1]) for entry in parse_block(text, brakets, delimiter) if len(entry['elems']) == 2]
