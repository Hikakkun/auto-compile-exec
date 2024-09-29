# auto-compile-exec

## 概要
このスクリプトは、指定されたディレクトリ内のCソースファイルを自動的にコンパイルし、実行結果を出力するためのツールです。スクリプトは、コンパイルおよび実行のタイムアウトを設定でき、結果をMarkdown形式で保存することができます。

## 改修案(2024/09/30)
* diffのOK/NGで再提出を決めるならjsonなどの構造化データでまとめたほうがいい気がする
* 各課題ごとにjsonを吐き出してコマンドラインorプログラムで確認
    * [jq コマンド](https://jqlang.github.io/jq/)
    * [jq コマンド マニュアル](https://jqlang.github.io/jq/manual/)
    * [jq コマンドを使う日常のご紹介(Qiita)](https://qiita.com/takeshinoda@github/items/2dec7a72930ec1f658af)
        * コマンドラインでjsonを整形 集計できる
* 提出されたプログラムは以下の通り
```json
{
    "programs" : {
        "student_numberA" : {
            "sources" : [
                "cのコード",
                "cのコード"
            ],  
            "compile_error":null,
            "execution" : [
                {
                    "in" : "",
                    "out" : "",
                    "expected" : null or string,
                    "diff" : null or string ,
                    "runtime_error" : null or srting
                }
            ]          
        },
        "student_numberB" : {
            "sources" : [
                "cのコード",
                "cのコード"
            ],  
            "compile_error":null,
            "execution" : [
                {
                    "in" : "",
                    "out" : "",
                    "expected" : null or string,
                    "diff" : null or string ,
                    "runtime_error" : null or srting
                }
            ]          
        },
    }
}
```
```json

```
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
python auto-compile-exec.py <target_dir> [-io or --input_output]  input_output_dir [-H or --header] header_dir [--nooutput]
```
* 引数
    * target_dir：Cソースファイルが含まれるディレクトリのパス。複数ディレクトリ指定可能
    * input_output_dir：オプション。入力ファイルと出力期待値ファイルが格納されているディレクトリ
        * in\d.txt out\d.txt のみを受付それぞれ一組とする
    * header_dir : オプション TA側が用意する.cと.hが格納されているディレクトリ
    * --nooutput：オプション。コンパイル結果をテキストファイルに出力せずにコンソールにのみ出力
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
    * `./auto-compile-exec.py ./example/header-submit-main/code -io ./example/header-submit-main/inout/ -H ./example/header-submit-main/header/`
1. 分割コンパイルを行いなおかつ入出力でdiffを取る
    * 学生が提出しているのは関数の実装
    * `./auto-compile-exec.py ./example/header-submit-func/code -io ./example/header-submit-func/inout/ -H ./example/header-submit-func/header/`
1. 提出が複数あるタイプで入出力でdiffを取る
    * `./auto-compile-exec.py ./example/submit-double/main ./example/submit-double/add ./example/submit-double/sub/ -H ./example/submit-double/header/ -io ./example/submit-double/inout/`
1. 結果をMarkdownに出力せずにコンパイルおよび実行
    * `./auto-compile-exec.py ./example/noinput-noheader/code --nooutput`
    * `./auto-compile-exec.py ./example/input-noheader/code -io ./example/input-noheader/inout/ --nooutput`

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