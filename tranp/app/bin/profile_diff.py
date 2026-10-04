import re
import sys
from typing import Any, ClassVar


class Args:
	"""引数"""

	def __init__(self, argv: list[str]) -> None:
		"""インスタンスを生成

		Args:
			argv: コマンドライン引数
		"""
		args = self.parse(argv)
		self.help: bool = args['help']
		self.a: str = args['a']
		self.b: str = args['b']
		self.target: str = args['target']

	def parse(self, argv: list[str]) -> dict[str, Any]:
		"""Args: argv: コマンドライン引数 Returns: 引数一覧"""
		args = {
			'help': False,
			'a': '',
			'b': '',
			'target': 'calls',
		}
		while argv:
			arg = argv.pop(0)
			if arg == '-h':
				args['help'] = True
			elif arg == '-t':
				args['target'] = argv.pop(0)
			else:
				args['a'] = arg
				args['b'] = argv.pop(0)

		return args


class App:
	"""アプリケーション"""

	def __init__(self, args: Args) -> None:
		"""インスタンスを生成

		Args:
			args: 引数
		"""
		self.args = args

	def run(self) -> None:
		"""実行処理"""
		if self.args.help:
			self.run_help()
		else:
			self.run_output()

	def run_help(self) -> None:
		"""実行処理(ヘルプ)"""
		print("""# Usage
$ bin/profile.sh -d profile_a.log profile_b.log
$ bin/profile.sh -d profile_a.log profile_b.log -t tot
$ bin/profile.sh -d profile_a.log profile_b.log -t cum
""")

	def run_output(self) -> None:
		"""実行処理"""
		a = self.parse_profile(self.load_file(self.args.a), self.args.target)
		b = self.parse_profile(self.load_file(self.args.b), self.args.target)
		self.dump(self.diff(a, b))

	def dump(self, diff: dict[str, float]) -> None:
		"""差分をダンプ

		Args:
			diff: 差分
		"""
		_diff = dict(reversed(sorted(diff.items(), key=lambda entry: entry[1])))
		diff_rank: dict[str, str] = {}
		for key, value in _diff.items():
			if isinstance(value, float):
				diff_rank[key] = '{:1.3f}'.format(value)
			else:
				diff_rank[key] = str(value)

		total = sum(_diff.values())
		print(f'total({self.args.target}):', total)
		print('-----')

		width = 0
		for file, calls in diff_rank.items():
			width = max(width, len(calls))

		for file, calls in diff_rank.items():
			indent = ' ' * (width - len(calls))
			print(f'{indent}{calls}', file)

	def load_file(self, filepath: str) -> str:
		"""ファイルをロード

		Args:
			filepath: ファイルパス
		Returns:
			コンテンツ
		"""
		with open(filepath, mode='r', encoding='utf-8') as f:
			return f.read()

	LinePattern: ClassVar = re.compile(r'\s*(\d+)(?:/\d+)?\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+) (.+)')
	PlacePattern: ClassVar = re.compile(r'([^:]+):\d+\(([^)]+)\)')

	def parse_profile(self, content: str, target: str) -> dict[str, float]:
		"""プロファイルをパース

		Args:
			content: コンテンツ
			target: 比較カラム
		Returns:
			プロファイル
		"""
		profile: dict[str, float] = {}
		for line in content.split('\n'):
			line_match = re.fullmatch(self.LinePattern, line)
			if not line_match:
				continue

			calls, tot, pertot, cum, percum, org_place = line_match.group(1, 2, 3, 4, 5, 6)

			# 'ファイル名(関数名)'に計測を統合
			place = org_place
			place_match = re.fullmatch(self.PlacePattern, org_place)
			if place_match:
				filename, func = place_match.group(1, 2)
				place = f'{filename}({func})'

			if target == 'calls':
				profile[place] = int(calls) + profile.get(place, 0) 
			elif target == 'tot':
				profile[place] = float(tot) + profile.get(place, 0.0)
			elif target == 'cum':
				profile[place] = float(cum) + profile.get(place, 0.0)

		return profile

	def diff(self, a: dict[str, float], b: dict[str, float]) -> dict[str, float]:
		"""プロファイル同士の差分を抽出

		Args:
			a: プロファイルA
			b: プロファイルB
		Returns:
			差分
		"""
		all_keys = set([*a.keys(), *b.keys()])
		results: dict[str, float] = {}
		for key in all_keys:
			diff = a.get(key, 0) - b.get(key, 0)
			if diff != 0:
				results[key] = diff

		return results


if __name__ == '__main__':
	args = Args(sys.argv[1:])
	App(args).run()
