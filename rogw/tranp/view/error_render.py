import os
import re

from rogw.tranp.lang.error import stacktrace
from rogw.tranp.syntax.node.node import Node


class ErrorRender:
	"""エラーレンダー"""

	def __init__(self, e: Exception) -> None:
		"""インスタンスを生成

		Args:
			e: 例外
		"""
		self.e = e

	def __str__(self) -> str:
		"""Returns: 文字列表現"""
		return self.render()

	def render(self) -> str:
		"""Returns: レンダリング結果"""
		traces = self.__build_stacktrace()
		quotation = self.__build_quotation()
		name = self.__build_name()
		message = self.__build_message()
		return f'{"\n".join([*traces, *quotation])}\n{name}: {message}'

	def __build_stacktrace(self) -> list[str]:
		"""Returns: スタックトレース"""
		pattern = re.compile(r'File "([^"]+)", line (\d+), in ([\w\d]+)')
		lines = ['Stacktrace:']
		root_dir = f'{os.getcwd()}{os.path.sep}'
		traces = stacktrace(self.e)
		for index, line in enumerate(traces):
			if index > 0 and line.startswith('Traceback'):
				wrap_last = traces[index - 3].split('\n')[1].strip()
				lines.append(f'    >>> {wrap_last}')
				lines.append(f'  {traces[index - 2].strip()}')
				continue

			matches = pattern.search(line)
			if not matches:
				continue

			fullpath, line_no, func_name = matches.group(1, 2, 3)
			filepath = fullpath.replace(root_dir, '')
			lines.append(f'  {filepath}:{line_no} {func_name}')

		last = traces[-2].split('\n')[1].strip()
		lines.append(f'    >>> {last}')
		return lines
	
	def __build_quotation(self) -> list[str]:
		"""Returns: エラー発生個所の引用"""
		if len(self.e.args) == 0 or not isinstance(self.e.args[0], Node):
			return []
		
		node = self.e.args[0]
		filepath = f'{node.module_path.replace('.', os.path.sep)}.py'
		if not os.path.exists(filepath):
			return []

		# XXX Larkのソースマップは+1されているため-1
		source_map = (
			node.source_map['begin'][0] - 1,
			node.source_map['begin'][1] - 1,
			node.source_map['end'][0] - 1,
			node.source_map['end'][1] - 1,
		)
		return self.Quotation(filepath, source_map).build()

	def __build_name(self) -> str:
		"""Returns: 例外モジュールパス"""
		return f'{self.e.__class__.__module__}.{self.e.__class__.__qualname__}'

	def __build_message(self) -> str:
		"""Returns: 例外メッセージ"""
		join_args = ', '.join([f'"{arg}"' if isinstance(arg, str) else str(arg) for arg in self.e.args])
		return f'({join_args})'

	class Quotation:
		"""引用ビルダー"""

		def __init__(self, filepath: str, source_map: tuple[int, int, int, int]) -> None:
			"""インスタンスを生成

			Args:
				filepath: ファイルパス
				source_map: ソースマップ
			"""
			self.filepath = filepath
			self.begin_line = source_map[0]
			self.cause_line = self.__load_line(filepath, self.begin_line)
			self.cause_range = self.__cause_range(source_map)

		def __load_line(self, filepath: str, line_no: int) -> str:
			"""該当行を読み込み

			Args:
				filepath: ファイルパス
				line_no: 行番号
			Returns:
				該当行
			"""
			with open(filepath, mode='rb') as f:
				lines = f.readlines()
				return lines[line_no].decode().replace('\n', '').replace('\t', ' ')

		def __cause_range(self, source_map: tuple[int, int, int, int]) -> tuple[int, int]:
			"""該当範囲を算出

			Args:
				source_map: ソースマップ
			Returns:
				該当範囲
			"""
			begin_line, begin_column, end_line, end_column = source_map
			diff = end_column - begin_column
			return (
				begin_column,
				begin_column + diff if begin_line == end_line else len(self.cause_line)
			)

		def build(self) -> list[str]:
			"""Returns: 該当行の引用"""
			line_no = self.begin_line + 1
			line_mark = self.__build_line_mark()
			return [
				f'via Node:',
				f'  {self.filepath}:{line_no}',
				f'    >>> {self.cause_line}',
				f'        {line_mark}',
			]

		def __build_line_mark(self) -> str:
			"""Returns: 該当行のマーク"""
			begin, end = self.cause_range
			indent = ' ' * begin
			# XXX 改行が対象の場合、差分が0になるため最小値を設ける
			explain = '^' * max(1, end - begin)
			return f'{indent}{explain}'
