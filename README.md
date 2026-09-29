tranp (TRANspiler on Python)
===

[![test](https://github.com/rog-works/tranp/actions/workflows/test.yml/badge.svg)](https://github.com/rog-works/tranp/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/rog-works/tranp/graph/badge.svg?token=Z1EGM7KUDJ)](https://codecov.io/gh/rog-works/tranp)
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

# 概要

* 言語非依存(※1)のトランスパイルフレームワーク
* 入力言語のAST(※2)を元に、出力言語のソースコードをレンダリング
* トランスパイルのリアルタイム変換や変換時のシンボル解析、ASTの解析ツールを付属
* ※1: 現状はPythonからC++への変換のみ実装
* ※2: ASTの生成は外部ツールを利用(自由に変更可能)

# 必須要件

* Python 3.13
* Lark 1.3.1
* Jinja2 3.1.4
* PyYAML 6.0.2

# インストール

```bash
$ pip install tranp
```

# トランスパイル (Python to C++)

## リアルタイム変換

* `-it`オプションを指定して実行することでREPLが起動します

```bash
$ tranp -it
```

* Pythonコードを入力した後、空行を入力するとトランスパイル結果がレンダリングされます

```bash
===============
Python code here. Type `exit` to quit:
a = 1
Result:
---------------
// @tranp.meta: {"version":"0.9.7","module":{"hash":"dummy","path":"__main__"},"transpiler":{"version":"0.9.0","module":"tranp.app.implements.cpp.transpiler.py2cpp.Py2Cpp"}}
#pragma once
int a = 1;
```

* 再びPythonコードを入力することで、繰り返し結果を確認することが可能です

```bash
===============
Python code here. Type `exit` to quit:
def main() -> int:
  return 1
Result:
---------------
// @tranp.meta: {"version":"0.9.7","module":{"hash":"dummy","path":"__main__"},"transpiler":{"version":"0.9.0","module":"tranp.app.implements.cpp.transpiler.py2cpp.Py2Cpp"}}
#pragma once
/** main */
int main() {
  return 1;
}
```

* `exit`のみ入力するとREPLが終了します

```bash
===============
Python code here. Type `exit` to quit:
exit
Quit
```

## 一括変換

* `-c`オプションでコンフィグを指定することで、設定に従って一括変換を行います
* [チュートリアル](#チュートリアル)で順を追って解説します

```bash
$ tranp -c path/to/config.yml
```

# チュートリアル

* 以下の様な構成のプロジェクトを用意します

```
app/
  sub.py
  main.py
config.yml
```

```python
# app/main.py
from app.sub import hello
def main() -> int:
  hello()
  return 1
```

```python
# app/sub.py
def hello() -> None:
  print('hello world!')
```

```yaml
# config.yml
grammar: data/grammar.lark
template_dirs:
  - data/cpp/template
trans_mapping: data/i18n.yml
input_globs:
  - app/**/*.py
output_dirs:
  - ./
output_language: cpp:h
exclude_patterns: []
env:
  transpiler:
    include_dirs:
      - app/
  view:
    immutable_param_types:
      - std::string
      - std::vector
      - std::map
      - std::function
```

* トランスパイルを実行します

```bash
$ tranp -c config.yml
```

* トランスパイルされたC++のソースコードは以下の様に配置されます

```
app/
  sub.py
  sub.h
  main.py
  main.h
config.yml
```

* トランスパイル結果は以下の様な内容になります

```cpp
// app/main.h
#include "app/sub.h"
/** main */
int main() {
  hello();
  return 1;
}
```

```cpp
// app/sub.py
/** hello */
void hello() {
  printf("hello world!");
}
```

# 解析ツール

## AST解析ツール

* `ast`コマンドを指定して実行するとREPLが起動します
* ※終了方法はトランスパイラーと同様

```bash
$ tranp ast
```

* Pythonコードを入力することでASTがレンダリングされます

```bash
==========
Code here. Type `exit` to quit:
a = 1
==========
AST
----------
file_input
  assign
    assign_namelist
      var
        name  2
    number    1
```

## ソースコード解析ツール

```bash
$ tranp analyze
```

# ライセンス

[MIT](LICENCE)
* tranpを用いて生成したトランスパイル後のソースコードに関してはライセンスに含まれません
