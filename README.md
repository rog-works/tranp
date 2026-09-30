tranp (TRANspiler on Python)
===

[![test](https://github.com/rog-works/tranp/actions/workflows/test.yml/badge.svg)](https://github.com/rog-works/tranp/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/rog-works/tranp/graph/badge.svg?token=Z1EGM7KUDJ)](https://codecov.io/gh/rog-works/tranp)
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

# 概要

* トランスパイルフレームワークのPython実装
* 入力言語のAST(※1)を元に、出力言語のソースコードをレンダリング
* ※1: ASTの生成はlarkを利用(自由に変更可能)

# 特徴

* 入出力言語を自由に選択可能(※1)
* テンプレート(※2)を変更することで、コア実装を改変することなく、レンダリング内容を自由に改変可能
* トランスパイルのリアルタイム変換・シンボル解析・AST解析ツールを付属

* ※1: 現状はPythonからC++への変換のみ実装
* ※2: テンプレートエンジンはJinja2を利用(自由に変更可能)

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

* `-it`オプションを指定して実行することでREPLが起動

```bash
$ tranp -it
```

* Pythonコードを入力した後、空行を入力するとトランスパイル結果がレンダリング

```bash
===============
Python code here. Type `exit` to quit:
a = 1
Result:
---------------
// @tranp.meta: {"version":"0.9.n","module":{"hash":"dummy","path":"__main__"},"transpiler":{"version":"0.9.n","module":"tranp.app.implements.cpp.transpiler.py2cpp.Py2Cpp"}}
#pragma once
int a = 1;
```

* 再びPythonコードを入力することで、繰り返し結果を確認することが可能

```bash
===============
Python code here. Type `exit` to quit:
def main() -> int:
  return 1
Result:
---------------
// @tranp.meta: {"version":"0.9.n","module":{"hash":"dummy","path":"__main__"},"transpiler":{"version":"0.9.n","module":"tranp.app.implements.cpp.transpiler.py2cpp.Py2Cpp"}}
#pragma once
/** main */
int main() {
  return 1;
}
```

* `exit`のみ入力するとREPLが終了

```bash
===============
Python code here. Type `exit` to quit:
exit
Quit
```

## 一括変換

* `-c`オプションでコンフィグを指定することで、設定に従って一括変換を行う
* [チュートリアル](#チュートリアル)で順を追って解説

```bash
$ tranp -c path/to/config.yml
```

# チュートリアル

* 以下の様な構成のプロジェクトを用意

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

* トランスパイルを実行

```bash
$ tranp -c config.yml
```

* トランスパイル後の配置

```
app/
  sub.py
  sub.h <- NEW!
  main.py
  main.h <- NEW!
config.yml
```

* トランスパイル結果

```cpp
// @tranp.meta: {"version":"0.9.n","module":{"hash":"6012cab9fec85852b56d7b7b8deb6bd9","path":"app.main"},"transpiler":{"version":"0.9.n","module":"tranp.app.implements.cpp.transpiler.py2cpp.Py2Cpp"}}
#pragma once
#include "sub.h"
/** main */
int main() {
	hello();
	return 1;
}
```

```cpp
// @tranp.meta: {"version":"0.9.n","module":{"hash":"96178f75f71ca63c3102afc3e041a5af","path":"app.sub"},"transpiler":{"version":"0.9.n","module":"tranp.app.implements.cpp.transpiler.py2cpp.Py2Cpp"}}
#pragma once
/** hello */
void hello() {
	printf("hello world!");
}

```

# 解析ツール

## AST解析ツール

* `ast`コマンドを指定して実行するとREPLが起動
* ※終了方法はトランスパイラーと同様

```bash
$ tranp ast
```

* Pythonコードを入力することでASTがレンダリング
* ※出力結果はlarkのASTに依存

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

## シンボル解析ツール

* `ast`コマンドを指定して実行するとREPLが起動
* 詳細は[シンボル解析ツール](docs/tool/analyze.md)で解説

```bash
$ tranp analyze
```

## ドキュメント

* [ドキュメント](docs/index.md)

# ライセンス

* [MIT](LICENCE)
* tranpを用いて生成したトランスパイル後のソースコードに関してはライセンスに含まれません
