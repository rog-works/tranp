プロファイリング
===

# 概要

* プロファイリング方法に関して記載

# 手法

1. time
2. cProfiler
3. pyinstruments

# 計測 - 1.time

* 古典的な方法
* 副作用が無いため、最も信頼できる結果

```sh
$ time bin/transpile.sh -f
$ time bin/test.sh
```

# 計測 - 2.cProfiler

* Python標準機能
* 実行速度が倍程度に増える
* 稀に計測されない実装パターンがあり、その影響で実行速度が大幅に変動(±)する場合がある

## トランスパイル

```sh
$ bin/transpile.sh -f -p tottime > profile_tottime.log
```

## テスト

### プロファイラーを有効化

```python
# tests/unit/rogw/tranp/implements/cpp/transpiler/test_py2cpp.py

@profiler(on=True)  # ← FalseからTrueに変更
@data_provider(...)
def test_exec(...) -> None:
  ...
```

### 実行

```sh
$ bin/test.sh tests/unit/rogw/tranp/implements/cpp/transpiler/test_py2cpp.py TestPy2Cpp test_exec > profile_tottime.log
```

# 計測 - 3.pyinstruments

* 外部パッケージ
* スタックトレース単位で結果を表示
* ボトルネックとなる個所が明白で分かりやすい

## venvアクティベート

```sh
$ .venv/bin/activate
```

## 実行

```sh
$ bin/profile.sh rogw/tranp/bin/transpile.py -f
```
