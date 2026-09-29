import sys

from tranp.app.bin.analyze import main as analyze
from tranp.app.bin.ast_check import main as ast_check
from tranp.app.bin.gram_check import main as gram_check
from tranp.app.bin.transpile import main as transpile


def main() -> None:
	"""エントリーポイント"""
	command = sys.argv[1]
	apps = {
		'transpile': transpile,
		'analyze': analyze,
		'ast': ast_check,
		'gram': gram_check,
	}
	apps.get(command, transpile)()


if __name__ == '__main__':
	main()
