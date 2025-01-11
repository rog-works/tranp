from rogw.tranp.compatible.cpp.classes import char


class String:
	"""文字列操作ユーティリティー"""

	@classmethod
	def count(cls, string: str, subject: str) -> int:
		"""指定の文字列が含まれる数を計測

		Args:
			string: 文字列
			subject: カウント対象の文字列
		Returns:
			int: 含まれる数
		Note:
			@see str.count
		"""
		index = 0
		count = 0
		while True:
			found = string.find(subject, index)
			if found == -1:
				break

			index = found + 1
			count += 1

		return count

	@classmethod
	def ltrim(cls, string: str, chara: char) -> str:
		"""トリム(左)

		Args:
			string: 文字列
			chara: 対象の文字
		Returns:
			str: トリム後の文字列
		"""
		found = -1
		for i in range(len(string)):
			if string[i] != chara:
				break

			found = i + 1

		if found == len(string):
			return ''

		return string[found:] if found != -1 else string

	@classmethod
	def rtrim(cls, string: str, chara: char) -> str:
		"""トリム(右)

		Args:
			string: 文字列
			chara: 対象の文字
		Returns:
			str: トリム後の文字列
		"""
		found = -1
		for i in range(len(string)):
			index = len(string) - 1 - i
			if string[index] != chara:
				break

			found = index

		if found == 0:
			return ''

		return string[:found] if found != -1 else string

	@classmethod
	def trim(cls, string: str, chara: char) -> str:
		"""トリム

		Args:
			string: 文字列
			chara: 対象の文字
		Returns:
			str: トリム後の文字列
		"""
		return cls.rtrim(cls.ltrim(string, chara), chara)

	@classmethod
	def is_number(cls, string: str, begin: int = -1, end: int = -1) -> bool:
		"""文字列が数字か判定

		Args:
			string: 文字列
			begin: 開始インデックス (default = -1)
			end: 終了インデックス (default = -1)
		Returns:
			bool: True = 数字
		"""
		if (begin == -1 and end == -1) or (begin >= 0 and end > begin):
			raise ValueError('Invalid arguments. begin: {begin}, end: {end}'.format(begin=begin, end=end))

		length = len(string)
		loops = min(length, end - begin) if end > 0 else length
		for index in range(loops):
			i = begin + index if begin >= 0 else index
			if index == 0 and string[i] == char('-'):
				continue

			if string[i] >= char('0') and string[i] <= char('9'):
				continue

			if string[i] == char('.'):
				continue

			return False

		return True

	@classmethod
	def join(cls, values: list[str], delimiter: str) -> str:
		"""区切り文字で文字列のリストを結合

		Args:
			values: 文字列リスト
			delimiter: 区切り文字
		Returns:
			str: 結合後の文字列
		Note:
			@see str.join
		"""
		join_values = ''
		for i in range(len(values)):
			if i > 0:
				join_values += delimiter + values[i]
			else:
				join_values += values[i]

		return join_values

	@classmethod
	def split(cls, src: str, delimiter: str) -> list[str]:
		"""区切り文字で文字列を分割する

		Args:
			src: 対象
			delimiter: 区切り文字
		Returns:
			list[str]: 分割した文字列
		Note:
			@see str.split
		"""
		parts: list[str] = []
		pos0 = 0
		while pos0 < len(src):
			pos1 = src.find(delimiter, pos0)
			if pos1 == -1:
				pos1 = len(src)

			parts.append(src[pos0:pos1])
			pos0 = pos1 + len(delimiter)

		# 対象の文字列が空文字、または末尾が区切り文字の場合は空文字を要素に追加する
		if len(src) == 0 or src.endswith(delimiter):
			parts.append('')

		return parts

	@classmethod
	def escape(cls, string: str, chara: char) -> str:
		"""文字列内の任意の文字に対してエスケープを施す

		Args:
			string: 対象
			chara: エスケープ対象の文字
		Returns:
			str: エスケープ後の文字列
		"""
		escaped = ''
		for i in range(len(string)):
			if string[i] == chara or string[i] == char('\\'):
				escaped += char('\\')

			escaped += string[i]

		return escaped

	@classmethod
	def unescape(cls, string: str) -> str:
		"""文字列内のエスケープを解除する

		Args:
			string: 対象
		Returns:
			str: エスケープ解除後の文字列
		"""
		unescaped = ''
		i = 0
		while i < len(string):
			if string[i] == char('\\'):
				unescaped += string[i + 1]
				i += 2
			else:
				unescaped += string[i]
				i += 1

		return unescaped
