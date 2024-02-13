import os
import subprocess

from rogw.tranp.app.io import appdir


def readline(prompt: str = '') -> str:
	if prompt:
		print(prompt)

	input_filepath = os.path.join(appdir(), 'bin/_input.sh')
	res = subprocess.run(['bash', input_filepath], stdout=subprocess.PIPE)
	return res.stdout.decode('utf-8').rstrip()
