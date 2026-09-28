def c_pragma(command: str) -> None:
	"""pragmaを埋め込む

	Args:
		command: コマンド
	Examples:
		```python
		# python
		pragma('once')
		```

		```cpp
		// cpp
		#pragma once
		```
	"""
	...


def c_include(command: str) -> None:
	"""includeを埋め込む

	Args:
		command: コマンド
	Examples:
		```python
		include('<stdio>')
		```

		```cpp
		#include <stdio>
		```
	"""
	...


def c_macro(command: str) -> None:
	"""マクロ呼び出しを埋め込む

	Args:
		command: コマンド
	Examples:
		```python
		# python
		macro('MACRO()')
		```

		```cpp
		MACRO()
		```
	"""
	...
