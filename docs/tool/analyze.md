ツール / シンボル解析ツール
===

# 概要

* シンボル解析ツール(REPL)

# 実行方法

```bash
$ tranp analyze
```

# 終了方法

* `exit`を入力 (または`Ctrl + C`)

```bash
--------------
Selection here. Type `exit` to quit:
exit
Quit
```

# タスクメニュー

```bash
==============
Task Menu
--------------
# Tasks
* (a)nalyze : Interactive Syntax Analyzer
* (c)lass   : Show Class Information
* (d)b      : Show Symbol DB
* (l)oad    : Load Module
* (p)retty  : Show AST
* (s)ymbol  : Show Symbol Information
* (h)elp    : Show Usage
--------------
@YYYY-MM-DD hh:mm:ss
--------------
Selection here. Type `exit` to quit:
```

* 括弧で囲われている1文字を入力することで、対応するタスクに遷移

|項目|コマンド|概要|
|---------------------|---|---|
| [analyze](#analyze) | a |ソースコードのリアルタイム解析|
| [class](#class)     | c |クラスシンボルのAST表示|
| [db](#db)           | d |シンボルの一覧表示|
| [load](#load)       | l |ソースコードの読み込み|
| [pretty](#pretty)   | p |モジュールのAST表示|
| [symbol](#symbol)   | s |シンボル情報の表示|
| help                | h |ヘルプ表示|

# analyze

* ソースコードを入力すると、モジュールのASTを表示
* 解析結果は`__main__`モジュールに登録。各タスクから解析が可能
* ※ソースコードは保存されない

```bash
==============
Python code here. Type `exit` to Menu:
a = 1
==============
AST
--------------
<Entrypoint: @0 __main__ (1, 1)..(2, 1)>
+-statements:
  +-<MoveAssign: @1 __main__#move_assign@1 (1, 1)..(1, 6)>
    +-receivers:
    | +-<DeclLocalVar: @3 __main__#a (1, 1)..(1, 2)>
    +-value: <Integer: @6 __main__#int@6 (1, 5)..(1, 6)>
```

# class

* 遷移後、ロード中の全モジュールのクラス一覧が表示

```bash
==============
Class List
--------------
tranp.app.compatible.libralies.type#type
collections.abc#Callable
collections.abc#Sequence
# ... 中略 ...
typing#Union
--------------
Class fullyname here:
```

* `Class List`に表示されている完全修飾名(`fullyname`)を入力

```bash
--------------
Class fullyname here:
typing#Union
--------------
<Class: @131 typing#Union (14, 1)..(17, 1)>
+-symbol: <TypesName: @134 typing#Union.Union (14, 7)..(14, 12)>
+-decorators:
+-template_params:
+-inherits:
+-inherit_sub_types:
+-comment: <Proxy: @132 typing#Union.Empty (0, 0)..(0, 0)>
+-statements:
  +-<Elipsis: @140 typing#Union.elipsis@140 (14, 14)..(14, 17)>
```

# db

* 遷移後、ロード中の全モジュールのシンボル一覧が表示

```bash
==============
Symbol DB
--------------
{
  "tranp.app.compatible.libralies.type#type.T": "tranp.app.compatible.libralies.type#type.T",
  "tranp.app.compatible.libralies.type#type": "tranp.app.compatible.libralies.type#type",
  "collections.abc#Callable": "collections.abc#Callable",
  # ... 中略 ...
  "tranp.app.compatible.libralies.classes#__name__": "tranp.app.compatible.libralies.classes#str"
}
```

# load

* 読み込むソースコードのファイルパスを入力 (実行ディレクトリーからの相対パス)
* 読み込みが完了すると、各タスクから解析が可能

```bash
--------------
Module filepath here:
example/json.py
--------------
Module load completed!
```

# pretty

* 遷移後、ロード中の全モジュールのモジュールパス一覧が表示

```bash
==============
Module List
--------------
tranp.app.compatible.libralies.type
tranp.app.compatible.libralies.classes
collections.abc
typing
--------------
Module path here:
```

* `Module List`に表示されているモジュールパスを入力

```bash
--------------
Module path here:
typing
==============
AST
--------------
<Entrypoint: @0 typing (1, 1)..(41, 1)>
+-statements:
  +-<Class: @1 typing#Annotated (1, 1)..(2, 1)>
  # ... 中略
  +-<TemplateClass: @375 typing#Self (40, 1)..(40, 23)>
    +-symbol: <AltTypesName: @377 typing#Self.Self (40, 1)..(40, 5)>
```

# symbol

* 遷移後、ロード中の全モジュールのモジュールパス一覧が表示

```bash
==============
Module List
--------------
tranp.app.compatible.libralies.type
tranp.app.compatible.libralies.classes
collections.abc
typing
--------------
Module path here:
```

* `Module List`に表示されているモジュールパスを入力

```bash
--------------
Module path here:
typing
==============
Node/Symbol fullyname or full_path or id here. Type `exit` to Menu:
```

* 選択したモジュール内のシンボルの完全修飾名/フルパス/ノードID(※1)のいずれかを指定
* ※1: class/db/prettyタスク等を利用して確認

```bash
==============
Node/Symbol fullyname or full_path or id here. Type `exit` to Menu:
typing#Any
{
  "Node": {
    "accessor": "public",
    "actual_symbol": "None",
    "alias_embedder": "None",
    "block": "<Block: @19 typing#Any.block@19 (2, 12)..(3, 1)>",
    "can_expand": "True",
    "class_methods": [],
    "class_vars": [],
    "classification": "class",
    "comment": "<Proxy: @12 typing#Any.Empty (0, 0)..(0, 0)>",
    "constructor_exists": "False",
    "decl_classes": "<generator object Class.decl_classes at 0x000002270B642340>",
    "decl_this_vars": "{}",
    "declare": "<Class: @11 typing#Any (2, 1)..(3, 1)>",
    "decorators": [],
    "depended_types": [],
    "domain_name": "Any",
    "full_path": "file_input.class_def[1]",
    "fullyname": "typing#Any",
    "id": "11",
    "inherit_sub_types": [],
    "inherits": [],
    "is_internal": "False",
    "methods": [],
    "module_path": "typing",
    "namespace": "typing",
    "operations": "<tranp.app.syntax.node.definition.accessible.PythonClassOperations object at 0x000002270B19F620>",
    "parent": "<Entrypoint: @0 typing (1, 1)..(41, 1)>",
    "scope": "typing",
    "source_map": "{'begin': (2, 1), 'end': (3, 1)}",
    "statements": [
      "<Elipsis: @20 typing#Any.elipsis@20 (2, 12)..(2, 15)>"
    ],
    "symbol": "<TypesName: @14 typing#Any.Any (2, 7)..(2, 10)>",
    "symbols": [
      "<TypesName: @14 typing#Any.Any (2, 7)..(2, 10)>"
    ],
    "tag": "class_def",
    "template_params": [],
    "this_vars": [],
    "tokens": "Any"
  },
  "Symbol": {
    "types_full_path": "file_input.class_def",
    "decl_full_path": "file_input.class_def",
    "shorthand": "type<Any>",
    "types": "<Class: @1 tranp.app.compatible.libralies.type#type (1, 1)..(2, 1)>",
    "decl": "<Class: @1 tranp.app.compatible.libralies.type#type (1, 1)..(2, 1)>",
    "node": "<Class: @11 typing#Any (2, 1)..(3, 1)>",
    "origin": "Reflection:type<T> at <Class: @1 tranp.app.compatible.libralies.type#type (1, 1)..(2, 1)>",
    "via": "Symbol:type at <Class: @1 tranp.app.compatible.libralies.type#type (1, 1)..(2, 1)>",
    "attrs": [
      "Reflection:Any at <Class: @11 typing#Any (2, 1)..(3, 1)>"
    ],
    "stacktrace": [
      "Reflection:type<Any> at <Class: @11 typing#Any (2, 1)..(3, 1)>",
      "Symbol:type at <Class: @1 tranp.app.compatible.libralies.type#type (1, 1)..(2, 1)>"
    ]
  }
}
```
