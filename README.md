Tranp (TRANslator on Python)
===

# Dependencies

* Python 3.10
* pip 22.2.1
* Lark 1.1.8

# Usage

## Install

```
$ pip install -r requirements.txt -t vendor/
```

## Symbol Analyzer Tool

```
$ bash bin/analyze.sh
```

## Transpile from Python to C++

```
$ bash bin/transpile.sh -i 'path/to/**/*.py' -o path/to
```

## Testing via tests/

```
$ bash bin/test.sh
```
