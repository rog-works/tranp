import os
import subprocess


def appdir() -> str:
	return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))


def readline(prompt: str = '') -> str:
	if prompt:
		print(prompt)

	input_filepath = os.path.join(appdir(), 'bin/_input.sh')
	res = subprocess.run(['bash', input_filepath], stdout=subprocess.PIPE)
	return res.stdout.decode('utf-8').rstrip()
