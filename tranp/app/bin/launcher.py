import sys

from tranp.app.bin.analyze import main as analyze
from tranp.app.bin.ast_check import main as ast_check
from tranp.app.bin.gram_check import main as gram_check
from tranp.app.bin.j2_check import main as j2_check
from tranp.app.bin.transpile import main as transpile


def help() -> None:
	"""ヘルプ"""
	print(
"""# Usage
$ tranp [sub-command default=transpile] [sub-command options...]
# Sub-Commands
transplie: Transpiler
  analyze: Symbol Analyzer
      ast: Syntax Analyzer
     gram: Grammer Analyzer
       j2: Jinja2 Analyzer
# Examples
$ tranp -h
$ tranp -it
$ tranp -c path/to/config.yml
$ tranp analyze
$ tranp ast
$ tranp gram
$ tranp j2
"""
	)


def main() -> None:
	"""エントリーポイント"""
	if len(sys.argv) == 1:
		help()
		return

	command = sys.argv[1]
	apps = {
		'-h': help,
		'transpile': transpile,
		'analyze': analyze,
		'ast': ast_check,
		'gram': gram_check,
		'j2': j2_check,
	}
	apps.get(command, transpile)()


if __name__ == '__main__':
	main()
