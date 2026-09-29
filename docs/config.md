トランスパイラー
===

# コンフィグ

## JSONSchema

```yaml
type: object
properties:
  grammar:
    type: string
    description: グラマーファイルのパス
  template_dirs:
    type: array
    description: テンプレートのフォルダー(読み取り順)
    items: string
  trans_mapping:
    type: string
    description: 翻訳ファイルのパス
  input_globs:
    type: array
    description: 入力ファイルの探索パターン
    items: string
  output_dirs:
    type: array
    description: 出力ディレクトリー
    items:
      type: string
      pattern: '[\w\d/]+(\*?:[\w\d/]+)'
  output_language:
    type: string
    description: 出力言語名(=拡張子)
    pattern: '[\w\d]+(:[\w\d]+)'
  exclude_patterns:
    type: array
    description: 入力ファイルの除外パターン
    items: string
  di:
    type: object
    description: DIシンボル
    additionalProperties:
      '[\w\d.]+': string
  env:
    type: object
    description: 変数
    properties:
      transpiler:
        type: object
        description: トランスパイラー用変数
        properties:
          include_dirs:
            type: array
            description: インクルードマッピング
            items:
              type: string
              pattern: '[\w\d./]+(:[\w\d./]+)?'
          cvars:
            type: object
            description: C++型変数の拡張定義
            additionalProperties:
              '[\w\d]+':
                pattern: '[\w\d]+'
          string_formats:
            type: object
            description: 文字列フォーマットマッピング
            additionalProperties:
              '[\w\d]+':
                pattern: '%\w+'
      view:
        type: object
        description: ビュー用変数
        properties:
          immutable_param_types:
            type: array
            description: 引数の暗黙的不変型
            items: string
        additionalProperties:
          '[\w\d]+': {}
```
