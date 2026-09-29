tranp (TRANspiler on Python)
===

[![test](https://github.com/rog-works/tranp/actions/workflows/test.yml/badge.svg)](https://github.com/rog-works/tranp/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/rog-works/tranp/graph/badge.svg?token=Z1EGM7KUDJ)](https://codecov.io/gh/rog-works/tranp)
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

# 概要

* 言語非依存(※1)のトランスパイルフレームワーク
* 入力言語のAST(※2)を元に、出力言語のソースコードをレンダリング
* トランスパイルのリアルタイム変換や変換時のシンボル解析、グラマー・ASTの解析ツールを付属
* ※1: 現状はPythonからC++への変換のみ実装
* ※2: ASTの生成は外部ツールを利用(自由に変更可能)

# 必須要件

* Python 3.13
* Lark 1.3.1
* Jinja2 3.1.4
* PyYAML 6.0.2

# インストール

```
$ pip install tranp
```

# 使用方法

## トランスパイラー (Python to C++)

```
$ tranp -c path/to/config.yml
```

## ソースコード解析ツール

```
$ tranp analyze
```

## グラマー解析ツール

```
$ tranp gram
```

## AST解析ツール

```
$ tranp ast
```

# ライセンス

[MIT](LICENCE)
* tranpを用いて生成したトランスパイル後のソースコードに関してはライセンスに含まれません
