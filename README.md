Tranp (TRANspiler on Python)
===

[![test](https://github.com/rog-works/tranp/actions/workflows/test.yml/badge.svg)](https://github.com/rog-works/tranp/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/rog-works/tranp/graph/badge.svg?token=Z1EGM7KUDJ)](https://codecov.io/gh/rog-works/tranp)

# Dependencies

* Python 3.12
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
