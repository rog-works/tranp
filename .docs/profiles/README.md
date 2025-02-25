プロファイリング
===

# 概要

* プロファイリング方法に関して記載

# 手法

1. time
2. cProfiler
3. pyinstruments

# 計測 - 1.time

## 概要

* 古典的な方法
* 副作用が無いため、最も信頼できる結果
* 実行時間しか計測できない

## 実行

```sh
$ time bin/transpile.sh -f
$ time bin/test.sh
```

# 計測 - 2.cProfiler

## 概要

* Python標準機能
* 実行速度が倍程度に増える
* 稀に計測されない実装パターンがあり、その影響で実行速度が大幅に変動(±)する場合がある
* 関数毎に計測し、結果を一覧で表示
* ソートはオプションによって切り替え

## ソート

* ncalls: 関数のコール数
* tottime: 対象の関数だけの消費時間
* cumtime: 対象の関数からの呼び出し時間も含めた消費時間

## 実行 - トランスパイル

```sh
$ bin/transpile.sh -f -p > profile_tottime.log
```

## 実行 - テスト

### プロファイラーの設定例

```python
# tests/unit/rogw/tranp/implements/cpp/transpiler/test_py2cpp.py

# フラグによって切り替え
@profiler(on=profiler_on)
@data_provider(...)
def test_exec(...) -> None:
  ...
```

### 実行

```sh
$ bin/test.sh -l -p > profile_tottime.log
```

# 計測 - 3.pyinstrument

## 概要

* 外部パッケージ
* スタックトレース単位で結果を表示
* ボトルネックとなる個所が明白で分かりやすい
* venvをアクティベートしないと使えない
* pyinstrumentsと言う非常によく似た名前のパッケージがあるがこちらは誤りなので注意

## 環境設定

```sh
# 仮想環境作成
$ python -m venv .venv

# venvアクティベート
$ . .venv/bin/activate

# インストール
(.venv) $ pip install pyinstrument
```

## 実行

```sh
# venvアクティベート
$ .venv/bin/activate

# 計測実行
(.venv) $ bin/profile.sh --show-all rogw/tranp/bin/transpile.py -f
```
