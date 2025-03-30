Tranp (TRANspiler on Python)
===

[![test](https://github.com/rog-works/tranp/actions/workflows/test.yml/badge.svg)](https://github.com/rog-works/tranp/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/rog-works/tranp/graph/badge.svg?token=Z1EGM7KUDJ)](https://codecov.io/gh/rog-works/tranp)

# Dependencies

* Python 3.13
* pip 22.2.1
* Lark 1.2.2
* Jinja2 3.1.4
* PyYAML 6.0.2

# Usage

## Install

```
$ pip install -r requirements.txt -t vendor/
```

## Grammar Analyzer Tool

```
$ bash bin/gram.sh
```

## AST Analyzer Tool

```
$ bash bin/ast.sh
```

## Symbol Analyzer Tool

```
$ bash bin/analyze.sh
```

## Transpile from Python to C++

```
$ bash bin/transpile.sh
```

## Testing via tests/

```
$ bash bin/test.sh
```
