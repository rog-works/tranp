def directive(command: str) -> None:
	"""ディレクティブを埋め込む
	トランスパイル後はcommandの内容がそのまま出力される

	Args:
		command (str): コマンド
	Examples:
		```python
		directive('#pragma once')
		```
	"""
	...
