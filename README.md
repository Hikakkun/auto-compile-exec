# auto-compile-exec

## 概要
このスクリプトは、指定されたディレクトリ内のCソースファイルを自動的にコンパイルし、実行結果を出力するためのツールです。スクリプトは、コンパイルおよび実行のタイムアウトを設定でき、結果をMarkdown形式で保存することができます。

## 環境構築
* python 3.10 以上
    * [typing.Optional](https://docs.python.org/ja/3/library/typing.html#typing.Optional), [with文のネスト](https://docs.python.org/ja/3/reference/compound_stmts.html#the-with-statement) を利用しているため
    * 3.12で実行確認済み
    * Linux, Max OSでは動くはず
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
    * target_dir：Cソースファイルが含まれるディレクトリのパス。
    * input_output_dir：オプション。入力ファイルと出力期待値ファイルが格納されているディレクトリ
        * in\d.txt out\d.txt のみを受付それぞれ一組とする
    * header_dir : オプション TA側が用意するプログラムが格納されているディレクトリ
    * --nooutput：オプション。コンパイル結果をテキストファイルに出力しない場合に指定します。
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
    * `./auto-compile-exec.py ./example/header-submit-func/code  -io  ./example/header-submit-func/inout/  -H  ./example/header-submit-func/header/`
1. 結果をmarkdownに出力せずにコンパイルおよび実行
    * `./auto-compile-exec.py ./example/noinput-noheader/code --nooutput`
    * `./auto-compile-exec.py ./example/input-noheader/code -io ./example/input-noheader/inout/ --nooutput`

## カスタマイズ
### タイムアウト
* 以下の変数の値を変更することで各タイムアウトの時間を変更可能
    * COMPILE_TIMEOTU : コンパイルの制限時間を設定
    * EXECUTION_TIMEOUT : プログラム実行時間の制限時間を設定
        * scanfに,が入っている or 無限ループプログラムを弾くため
```python
# 各種タイムアウト時間を設定
COMPILE_TIMEOTU = 2
EXECUTION_TIMEOUT = 2
```


### コンパイル対象ファイル
* auto_compile_exec関数内の`target_file_list`を変更することでループを回す対象を変更可能
* 学生記番号 `{"01234567", "01234568"}` をターゲットにしたい場合
```python
def auto_compile_exec(
    target_dir: Path,
    compile_timeout: int,
    execution_timeout: int,
    intput_output_dir: Path | None = None,
    header_dir: Path | None = None,
):
    # 省略

    c_files : list[Path] = list(target_dir.rglob("*.c"))
    # 対象ファイルを変えたい場合はこの部分を変更
    # target_file_list = sorted(c_files)
    student_set = {"01234567", "01234568"}
    target_file_list = filter(lambda file: file.stem in student_set, c_files)
```