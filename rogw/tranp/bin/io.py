import os
import subprocess

from rogw.tranp.app.dir import tranp_dir


def readline(prompt: str = '') -> str:
	"""ユーザーの入力待ち受け、入力値を取得

	Args:
		prompt: 確認メッセージ
	Returns:
		str: 入力値
	Note:
		Linux環境でカーソル移動を実現するため、サブプロセス経由でBashスクリプトを実行する
	"""
	if prompt:
		print(prompt)

	input_filepath = os.path.join(tranp_dir(), 'bin/_input.sh')
	res = subprocess.run(['bash', input_filepath], stdout=subprocess.PIPE)
	return res.stdout.decode('utf-8').rstrip()
