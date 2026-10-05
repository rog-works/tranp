tranp (TRANspiler on Python)
===

[![test](https://github.com/rog-works/tranp/actions/workflows/test.yml/badge.svg)](https://github.com/rog-works/tranp/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/rog-works/tranp/graph/badge.svg?token=Z1EGM7KUDJ)](https://codecov.io/gh/rog-works/tranp)
[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

# 概要

* Pythonで実装されたトランスパイルフレームワーク
* 入力言語のソースコードからAST(※1)を生成・解析し、テンプレート(※2)を介して出力言語のソースコードを出力するCLIツール

```
※1: ASTの生成はLarkを利用(自由に変更可能)
※2: テンプレートエンジンはJinja2を利用(自由に変更可能)
```

# 特徴

* 入力・出力言語共に自由に選択できる設計(※1)
* テンプレートを変更することで、コア実装を改変することなくレンダリング内容を自由に改変可能
* 難読化されない可読なソースコードを生成
* 型注釈の解析と型推論の組み合わせによる型の補完に対応
* トランスパイルのリアルタイム変換(REPL)が可能
* シンボル解析・AST解析のツールを付属

```
※1: 現状はPythonからC++への変換のみ実装。新しい組み合わせは個別に実装が必要であり、決して容易ではない点に注意
```

# 必須要件

* Python 3.13
* [Lark](https://lark-parser.readthedocs.io/en/latest/index.html) 1.3.1
* [Jinja2](https://github.com/pallets/jinja) 3.1.4
* [PyYAML](https://pypi.org/project/PyYAML/) 6.0.2

# 動作環境

* Linux
* Unix系(MacOSなど)
* Windows ※1

```
※1: WindowsではREPLが使用不可 (WSL/Git Bash等の互換環境を使用すれば可能)
```

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
==========
Code here. Type `exit` to quit:
a = 1
==========
Result:
----------
// @tranp.meta: {"version":"0.9.n","module":{"hash":"dummy","path":"__main__"},"transpiler":{"version":"0.9.n","module":"tranp.app.implements.cpp.transpiler.py2cpp.Py2Cpp"}}
#pragma once
int a = 1;
```

* 再びPythonコードを入力することで、繰り返し結果を確認することが可能

```bash
==========
Code here. Type `exit` to quit:
def main() -> int:
  return 1
==========
Result:
----------
// @tranp.meta: {"version":"0.9.n","module":{"hash":"dummy","path":"__main__"},"transpiler":{"version":"0.9.n","module":"tranp.app.implements.cpp.transpiler.py2cpp.Py2Cpp"}}
#pragma once
/** main */
int main() {
  return 1;
}
```

* `exit`のみ入力するとREPLが終了 (または`Ctrl + C`)

```bash
==========
Code here. Type `exit` to quit:
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
grammar: ${tranp_dir}/data/grammar.lark
trans_mapping: ${tranp_dir}/data/i18n.yml
template_dirs:
  - ${tranp_dir}/data/cpp/template
input_globs:
  - app/**/*.py
exclude_patterns: []
output_dirs:
  - ./
output_language: cpp:h
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
* ※出力結果はLarkのASTに依存

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

* `analyze`コマンドを指定して実行するとREPLが起動
* 詳細は[シンボル解析ツール](docs/tool/analyze.md)で解説

```bash
$ tranp analyze
```

# ドキュメント

* [ドキュメント](docs/index.md)

# 互換性

* 本プロジェクトは実験的なプロジェクトであり、作者自身の課題を解決するために開発しています
* 事前の告知なく破壊的な仕様変更を行う可能性があり、バージョン毎の互換性を保証するものではない旨、予めご了承ください
* 継続的な利用にあたってはバージョンを固定することを推奨します

# ライセンス

* [MIT](LICENCE)
* tranpを用いて生成したトランスパイル後のソースコードに関してはライセンスに含まれません
