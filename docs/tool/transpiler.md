ツール / トランスパイラー

# 使用方法

```bash
# リアルタイム変換(REPL)
$ tranp -it

# リアルタイム変換(REPL/コンフィグ指定)
$ tranp -it -c config.yml

# トランスパイル(一括変換)
$ tranp -c config.yml

# トランスパイル(一括変換/再出力)
$ tranp -c config.yml -f

# トランスパイル(単体変換)
$ tranp -c config.yml -i main.py

# トランスパイル(ログ出力)
$ tranp -c config.yml -v

# トランスパイル(プロファイル出力)
$ tranp -c config.yml -p
```

# キャッシュ

* ツールの起動、またはトランスパイルを実行すると実行ディレクトリー配下にキャッシュ(`.cache/`)が生成される
* 高速化のために自動的に生成されるため、不要であれば削除して問題ない
