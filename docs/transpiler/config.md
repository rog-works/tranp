トランスパイラー / コンフィグ
===

# 概要

* コンフィグの仕様・スキーマに関して記載

# インデックス

* [grammar](#grammar)
* [template_dirs](#template_dirs)
* [trans_mapping](#trans_mapping)
* [input_globs](#input_globs)
* [output_dirs](#output_dirs)
* [exclude_patterns](#exclude_patterns)
* [di](#di)
* env
  * transpiler
    * [include_dirs](#include_dirs)
    * [cvars](#cvars)
    * [string_formats](#string_formats)
  * [view](#view)
    * [immutable_param_types](#immutable_param_types)
* [JSONSchema](#jsonschema)

# grammer

* グラマーファイルのパス

## ファイルの種類

* シンタックスパーサーに準拠
* デフォルトは`.lark`

## 書式

```yaml
type: string
pattern: '[\w\d/.]+'
```

## 設定例

```yaml
grammar: path/to/grammar.lark
```

# trans_mapping

* 翻訳ファイルのパス

## ファイルの種類

* `.yml`固定

## 書式

```yaml
type: string
pattern: '[\w\d/.]+\.yml'
```

## 設定例

```yaml
trans_mapping: data/i18n.yml
```

# template_dirs

* テンプレートの探索フォルダーのリスト
* 定義順にファイルを探索

## ファイルの種類

* レンダラーに準拠
* デフォルトは`.j2`

## 書式

```yaml
type: array
items:
  type: string
  pattern: '[\w\d/]+'
```

## 設定例

```yaml
template_dirs:
  - data/template
  - data/cpp/template
```

# input_globs

* 入力ソースコードの探索globパターンのリスト

## ファイルの種類

* 入力言語に依存

## 書式

```yaml
type: array
items:
  type: string
  pattern: '[\w\d/.*]+'
```

## 設定例

```yaml
input_globs:
  - src/**/*.py
```

# exclude_patterns

* 入力ソースコードの除外パターンのリスト
* ワイルドカードが使用可能 ※globや正規表現は不可

## 書式

```yaml
type: array
items:
  type: string
  pattern: '[\w\d/.]+\*?'
```

## 設定例

```yaml
exclude_patterns:
  - external/*
```

# output_dirs

* 出力フォルダーのマッピングリスト
* 書式により出力先を変更
* 1件以上の設定が必須

## 書式

```yaml
type: array
minItems: 1
items:
  type: string
  pattern: '[\w\d/.]+(\*?:[\w\d/.]+)?'
```

### パターンA (`./`)

* 入力ファイルと同じ場所に出力
* 変換例: `path/to/a.py` -> `path/to/a.h`

### パターンB (`from/:path/to`)

* 前方一致した左辺を右辺に置換
* 変換例: `from/a.py` -> `path/to/a.h`

### パターンC (`from/*:path/to`)

* 右辺に入力パスを加えたパスに変換
* 変換例: `from/a.py` -> `path/to/from/a.h`

## 設定例

```yaml
output_dirs:
  - ./
```

# output_language

* 出力言語名(=出力ファイルの拡張子)
* 書式により出力拡張子を変更

## 書式

```yaml
type: string
pattern: '[\w\d]+(:[\w\d]+)?'
```

### パターンA (`cpp`)

* そのまま出力
* 変換例: `a.py` -> `a.cpp`

### パターンB (`cpp:h`)

* 右辺の拡張子で出力
* 変換例: `a.py` -> `a.h`

## 設定例

```yaml
output_language: cpp:h
```

# di

* DIシンボルの拡張定義
* キー: 対象のDIシンボルのモジュールパス
* 値: 注入するクラス・関数のモジュールパス

## 書式

```yaml
type: object
additionalProperties:
  '[\w\d.]+':
    type: string
    pattern: '[\w\d.]+'
```

## 設定例

```yaml
di:
  tranp.app.view.render.RendererHelperProvider: view.my_helper_provider
```

# include_dirs

* インクルードパスの変換パターンリスト
* 書式により変換パターンを変更

## 書式

```yaml
type: array
items:
  type: string
  pattern: '[\w\d/]+(:[\w\d/]+)?'
```

### パターンA (`starts/`)

* 前方一致した階層を除去
* 変換例: `starts/a.h` -> `a.h`

### パターンB (`starts/:replace/`)

* 前方一致した左辺を右辺に置換
* 変換例: `starts/a.h` -> `replace/a.h`

## 設定例

```yaml
include_dirs:
  - src/
```

# cvars

* C++型変数の拡張定義
* 登録した型は規定のC++型変数と透過的に扱われる

## 書式

```yaml
type: object
additionalProperties:
  '[\w\d]+':
    type: string
    pattern: '(CP|CW|CSP|CWP|CUP|CRef)(Const)?'
```

## 設定例

```yaml
cvars:
  MyPtr: CSP
```

# string_formats

* 文字列フォーマッターの書式設定
* 登録した型を`string.format`の実引数に指定した際に利用

## 書式

```yaml
type: object
additionalProperties:
  '[\w\d]+':
    type: string
    pattern: '%\w+'
```

## 設定例

```yaml
string_formats:
  MyPtr: '%p'
```

# view

* ビュー用の環境変数
* テンプレート内で`get_env`ヘルパーを介して参照可能

## 書式

```yaml
type: object
additionalProperties:
  '[\w\d]+': {}
```

## 設定例

```yaml
view:
  app_name: 'Myアプリケーション'
```

# immutable_param_types

* 引数の暗黙的不変型のリスト
* ビュー用の環境変数の一部
* 登録された型を引数にした場合、仮引数の型を不変型としてトランスパイル

## 書式

```yaml
type: array
items:
  type: string
  pattern: '[\w\d.:\[\]]+'
```

## 設定例

```yaml
immutable_param_types:
  - std::string
  - std::vector
  - std::map
  - std::function
```

# JSONSchema

```yaml
type: object
properties:
  grammar:
    type: string
    pattern: '[\w\d/.]+'
  trans_mapping:
    type: string
    pattern: '[\w\d/.]+\.yml'
  template_dirs:
    type: array
    items:
      type: string
      pattern: '[\w\d/.]+'
  input_globs:
    type: array
    items:
      type: string
      pattern: '[\w\d/.*]+'
  exclude_patterns:
    type: array
    items:
      type: string
      pattern: '[\w\d/.]+\*?'
  output_dirs:
    type: array
    minItems: 1
    items:
      type: string
      pattern: '[\w\d/.]+(\*?:[\w\d/.]+)'
  output_language:
    type: string
    pattern: '[\w\d]+(:[\w\d]+)'
  di:
    type: object
    additionalProperties:
      '[\w\d.]+':
        type: string
        pattern: '[\w\d.]+'
  env:
    type: object
    properties:
      transpiler:
        type: object
        properties:
          include_dirs:
            type: array
            items:
              type: string
              pattern: '[\w\d/]+(:[\w\d/]+)?'
          cvars:
            type: object
            additionalProperties:
              '[\w\d]+':
                type: string
                pattern: '(CP|CW|CSP|CWP|CUP|CRef)(Const)?'
          string_formats:
            type: object
            additionalProperties:
              '[\w\d]+':
                type: string
                pattern: '%\w+'
      view:
        type: object
        properties:
          immutable_param_types:
            type: array
            items:
              type: string
              pattern: '[\w\d.:\[\]]+'
        additionalProperties:
          '[\w\d]+': {}
```
