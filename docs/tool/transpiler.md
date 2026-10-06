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

* 解析ツールの起動、またはトランスパイルを実行すると実行ディレクトリー配下にキャッシュ(`.cache/`)が生成されます
* キャッシュにはASTやシンボルの解析結果が保存されており、再実行時の高速化を目的に生成しています
* 自動的に生成されるため、不要であれば削除して問題ありません
