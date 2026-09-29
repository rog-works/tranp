import subprocess


def readline(prompt: str = '') -> str:
	"""ユーザーの入力待ち受け、入力値を取得

	Args:
		prompt: 確認メッセージ
	Returns:
		入力値
	Note:
		Linux環境でカーソル移動を実現するため、サブプロセス経由でBashスクリプトを実行する
	"""
	if prompt:
		print(prompt)

	return subprocess.run(['bash', '-c', 'IFS= read -e input; echo "${input}"'], stdout=subprocess.PIPE, text=True).stdout.rstrip()


def tty(prompt: str = '') -> list[str]:
	"""対話モードで入力を受け付け。空行、または`exit`を入力することで終了

	Args:
		prompt: 確認メッセージ
	Returns:
		入力値リスト
	"""
	if prompt:
		print(prompt)

	lines: list[str] = []
	while True:
		line = readline()
		if not line:
			break
		elif line == 'exit':
			return ['exit']

		lines.append(line)

	return lines
