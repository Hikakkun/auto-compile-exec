# auto-compile-exec

## 概要
このスクリプトは、指定されたディレクトリ内のCソースファイルを自動的にコンパイルし、実行結果を出力するためのツールです。スクリプトは、コンパイルおよび実行のタイムアウトを設定でき、結果をjsonもしくはMarkdown形式で保存することができます。

## 改修案(2024/09/30)
* diffのOK/NGで再提出を決めるならjsonなどの構造化データでまとめたほうがいい気がする
* 各課題ごとにjsonを吐き出してコマンドラインorプログラムで確認
    * [jq コマンド](https://jqlang.github.io/jq/)
    * [jq コマンド マニュアル](https://jqlang.github.io/jq/manual/)
    * [jq コマンドを使う日常のご紹介(Qiita)](https://qiita.com/takeshinoda@github/items/2dec7a72930ec1f658af)
        * コマンドラインでjsonを整形 集計できる

## 環境構築
* python 3.10 以上
    * [typing.Optional(型ヒント)](https://docs.python.org/ja/3/library/typing.html#typing.Optional), [with文のネスト](https://docs.python.org/ja/3/reference/compound_stmts.html#the-with-statement) を利用しているため
    * 3.12で実行確認済み
    * Linux, Mac OSでは動くはず
        * Mac OSはバージョンによってプリインストールのPythonバージョンが3.9のことがあるのでbrewで3.10以上をインストールしてください
    * Windowsでは動作検証していないがPythonにパスが通っていれば動くはず
* clang-format
    * 各sourceを出力するときに使用
    * 生徒のコードを自動でフォーマットしてくれる
    * clang-format が見つからない場合はcatを使うためインストールしていなくとも使える
    * 以下の方法でインストール可能
        * linux `sudo apt install clang-format`
        * mac `brew install clang-format`

## 使用方法
* 以下のコマンドを実行してスクリプトを使用します：

```sh
> python auto-compile-exec.py -h
usage: ace.py [-h] [-io INPUT_OUTPUT] [-I INCLUDE] [-sn STUDENT_NUMBER] [--nodiff] [--output_markdown] [--uninitialized_error] target_dir [target_dir ...]

学生のプログラムを自動でコンパイルし、テストを実行するスクリプトです。指定したディレクトリ内のCソースコードをコンパイルし、必要に応じて入出力ファイルを用いた実行を行い、結果を収集します。

positional arguments:
  target_dir            ソースコードが含まれるディレクトリのパスを1つ以上指定してください。

options:
  -h, --help            show this help message and exit
  -io INPUT_OUTPUT, --input_output INPUT_OUTPUT
                        入出力テストデータ（入力ファイルと期待される出力ファイル）が含まれるディレクトリのパス。
  -I INCLUDE, --include INCLUDE
                        事前に準備されたCファイルを含むディレクトリのパス。
  -sn STUDENT_NUMBER, --student_number STUDENT_NUMBER
                        学生番号をパイプ(|)区切りで指定します。指定しない場合はconfig.iniから読み取ります。
  --nodiff              出力の差分チェックをスキップする場合に使用します。
  --output_markdown     コンパイル結果をテキストファイルに出力しない場合に使用します。
  --uninitialized_error
                        未初期化変数に関するエラーを強制するためのオプションです。
```
* config.ini が存在し DEFAULT StudentList に配列形式で学籍番号を記入している場合その学生のみがコンパイルのターゲットとなる
    * config.ini が存在しない or  config.ini の書き方が間違えている場合はtarget_dir すべてがコンパイルの対象になる 
```ini:config.ini
[DEFAULT]
StudentList = ["00001111", "00001112"]
```

### 使用例
* repository内のexampleで動作確認可能
    * git clone していればrepository rootで以下を実行可能
    * `chmod +x auto-compile-exec.py` すると`python *.py`しなくて動く
1. 単体のソースファイルのみコンパイルし結果を表示
    * `./auto-compile-exec.py ./example/noinput-noheader/code`
1. 単体のソースファイルのみコンパイルし入出力でdiffを取る
    * `./auto-compile-exec.py ./example/input-noheader/code -io ./example/input-noheader/inout/`
1. 分割コンパイルを行いなおかつ入出力でdiffを取る
    * 学生が提出しているのはmian関数が含まれているパターン
    * `./auto-compile-exec.py ./example/header-submit-main/code -io ./example/header-submit-main/inout/ -I ./example/header-submit-main/header/`
1. 分割コンパイルを行いなおかつ入出力でdiffを取る
    * 学生が提出しているのは関数の実装
    * `./auto-compile-exec.py ./example/header-submit-func/code -io ./example/header-submit-func/inout/ -I ./example/header-submit-func/header/`
1. 提出が複数あるタイプで入出力でdiffを取る
    * `./auto-compile-exec.py ./example/submit-double/main ./example/submit-double/add ./example/submit-double/sub/ -I ./example/submit-double/header/ -io ./example/submit-double/inout/`
2. 結果をJSONではなくMarkdownで出力
    * `./auto-compile-exec.py ./example/noinput-noheader/code --output_markdown`
    * `./auto-compile-exec.py ./example/input-noheader/code -io ./example/input-noheader/inout/ --output_markdown`
3. 未初期化の変数がある場合コンパイル時にエラー発生
    * `./auto-compile-exec.py ./example/noinput-noheader/code --uninitialized_error`
    * `./auto-compile-exec.py ./example/input-noheader/code -io ./example/input-noheader/inout/ --uninitialized_error`
4. diffを取らない
    * `./auto-compile-exec.py ./example/noinput-noheader/code --nodiff `
    * `./auto-compile-exec.py ./example/input-noheader/code -io ./example/input-noheader/inout/ --nodiff `

### 出力JSON
* JSON Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "patternProperties": {
    "^[0-9]+$": {
      "type": "object",
      "properties": {
        "source": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "ソースコードの文字列の配列"
        },
        "compile_error": {
          "type": ["string", "null"],
          "description": "コンパイルエラーのメッセージ。エラーがない場合はnull"
        },
        "execution": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "in": {
                "type": ["string", "null"],
                "description": "入力データ。入力データがない場合はnull"
              },
              "out": {
                "type": ["string", "null"],
                "description": "プログラムの出力。出力がない場合はnull"
              },
              "expected": {
                "type": ["string", "null"],
                "description": "期待される出力。期待出力がない場合はnull"
              },
              "diff": {
                "type": ["string", "null"],
                "description": "出力と期待される出力の差分。差異がない場合はnull"
              },
              "runtime_error": {
                "type": ["string", "null"],
                "description": "実行時エラーの情報。エラーがない場合はnull"
              }
            },
            "required": ["in", "out", "expected", "diff", "runtime_error"],
            "additionalProperties": false,
            "description": "各テストケースの実行結果"
          },
          "description": "実行結果のオブジェクトの配列"
        }
      },
      "required": ["source", "compile_error", "execution"],
      "additionalProperties": false,
      "description": "各学生のデータを格納するオブジェクト"
    }
  },
  "additionalProperties": false,
  "description": "学生番号をキーとした全体のデータ構造"
}
```
* 具体例
```json
{
  "0000001": {
    "source": [
      "//example/submit-double/main/0000001.c\n#include \"operator.h\"\n..."
    ],
    "compile_error": null,
    "execution": [
      {
        "in": "3 1",
        "out": "4\n2\n3\n3\n-2\n",
        "expected": "4\n2\n3\n3\n-2",
        "diff": null,
        "runtime_error": null
      },
      {
        "in": "4 5",
        "out": "9\n-1\n20\n0\n1\n",
        "expected": "9\n-1\n20\n0\n1",
        "diff": null,
        "runtime_error": null
      }
    ]
  }
}
```

### 出力JSONフィルタリング
* コマンドラインでJSONを集計, フィルタリングできるツール
  * [jq コマンド](https://jqlang.github.io/jq/)
  * [jq コマンド マニュアル](https://jqlang.github.io/jq/manual/)
  * [jq コマンドを使う日常のご紹介(Qiita)](https://qiita.com/takeshinoda@github/items/2dec7a72930ec1f658af)
* `./auto-compile-exec.py` を用いて出力されたJSONを`out.json`とする
```bash
# コンパイルエラーが発生 or diffが違う or 実行時エラーが発生 の生徒のフィルタリング
jq 'to_entries | map(select(.value.compile_error != null or (.value.execution | any(.diff != null or .runtime_error != null)))) | map({(.key): .value}) | add' out.json
# コンパイルエラーが発生した生徒をフィルタリング
jq 'to_entries | map(select(.value.compile_error != null)) | map({(.key): .value}) | add' out.json
# diffが違う生徒をフィルタリング
jq 'to_entries | map(select(.value.execution | any(.diff != null))) | map({(.key): .value}) | add'
# 実行時エラーが発生した生徒をフィルタリング
jq 'to_entries | map(select(.value.execution | any(.runtime_error != null))) | map({(.key): .value}) | add'
# 問題のない生徒をフィルタリング
jq 'to_entries | map(select(.value.compile_error == null and (.value.execution | all(.diff == null and .runtime_err or == null)))) | map({(.key): .value}) | add' out.json 
```
* パイプ `|` でつないで実行
```bash 
# example/submit-double 内をコンパイルして実行
# jqで問題のある生徒をフィルタリング
# markdownに変換
./auto-compile-exec.py example/submit-double/main example/submit-double/add example/submit-double/sub -I example/submit-double/header/ -io example/submit-double/inout/ | jq 'to_entries | map(select(.value.compile_error != null or (.value.execution | any(.diff != null or .runtime_error != null)))) | map({(.key): .value}) | add' | ./convert_md.py > error.md
```
## カスタマイズ
### タイムアウト
* 以下の変数の値を変更することで各タイムアウトの時間を変更可能
    * COMPILE_TIMEOTU : コンパイルの制限時間を設定
    * EXECUTION_TIMEOUT : プログラム実行時間の制限時間を設定
        * 無限ループプログラムを弾くため
```python
# 各種タイムアウト時間を設定
COMPILE_TIMEOTU = 2
EXECUTION_TIMEOUT = 2
```

## gcc
* このような構造の場合
```bash
├── code
│   ├── 00000001.c  //haader内の関数を用いて計算
│   ├── 00000002.c
│   └── 00000003.c
└── header          //簡単な演算を定義
    ├── add.c
    ├── dev.c
    ├── mul.c
    ├── operator.h
    └── sub.c
```
* 以下のようなコマンドで`00000001.c`をコンパイル可能
    * `gcc -I header/ code/00000001.c  header/add.c header/dev.c header/mul.c header/sub.c`
        * -I オプションをつけないと `code/00000001.c` が ` #include "operator.h"` を見つられずにエラー
        ```basu 
        > gcc  code/main0.c  header/add.c header/dev.c header/mul.c header/sub.c
        code/main0.c:2:10: fatal error: operator.h: No such file or directory
            2 | #include "operator.h"
            |          ^~~~~~~~~~~~
        compilation terminated.
        ```
* `header/` 以下のソースは事前にコンパイルしておくと効率的
    * 以下を実行した後に
        * `gcc -I header/ -c  header/add.c -o header/add.o` 
        * `gcc -I header/ -c  header/sub.c -o header/sub.o`
        * `gcc -I header/ -c  header/dev.c -o header/dev.o`
        * `gcc -I header/ -c  header/mul.c -o header/mul.o`
    * `gcc -I header/ code/main0.c header/add.o header/dev.o header/mul.o header/sub.o`
* 提出ファイルが複数ある場合も同様に
```bash
├── main
│   ├── 00000001.c  //haader内の関数を用いて計算
│   ├── 00000002.c
│   └── 00000003.c
├── add
│   ├── 00000001.c  //add関数を実装
│   ├── 00000002.c
│   └── 00000003.c
└── header          //簡単な演算を定義
    ├── dev.c
    ├── mul.c
    ├── operator.h
    └── sub.c
```
* `gcc -I header/ main/00000001.c add/00000001.c header/dev.c header/mul.c header/sub.c`
* もしくは `header/` 以下をコンパイルして `gcc -I header/ main/00000001.c add/00000001.c header/dev.o header/mul.o header/sub.o` 