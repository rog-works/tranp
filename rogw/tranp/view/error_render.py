import os
import re
from rogw.tranp.lang.error import stacktrace


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
		name = self.__build_name()
		message = self.__build_message()
		return f"""Stacktrace:
  {'\n  '.join(traces)}
{name}: {message}"""

	def __build_stacktrace(self) -> list[str]:
		"""Returns: スタックトレース"""
		pattern = re.compile(r'File "([^"]+)", line (\d+), in ([\w\d]+)')
		lines: list[str] = []
		root_dir = f'{os.getcwd()}{os.path.sep}'
		for line in stacktrace(self.e):
			matches = pattern.search(line)
			if not matches:
				continue

			fullpath, lineno, funcname = matches.group(1, 2, 3)
			filepath = fullpath.replace(root_dir, '')
			lines.append(f'{filepath}:{lineno} {funcname}')

		return lines

	def __build_name(self) -> str:
		"""Returns: 例外モジュールパス"""
		return f'{self.e.__class__.__module__}.{self.e.__class__.__qualname__}'

	def __build_message(self) -> str:
		"""Returns: 例外メッセージ"""
		join_args = ', '.join([f'"{arg}"' if isinstance(arg, str) else str(arg) for arg in self.e.args])
		return f'({join_args})'
