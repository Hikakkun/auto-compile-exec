# auto-compile-exec

## 概要
このスクリプトは、指定されたディレクトリ内のCソースファイルを自動的にコンパイルし、実行結果を出力するためのツールです。スクリプトは、コンパイルおよび実行のタイムアウトを設定でき、結果をMarkdown形式で保存することができます。

## 環境構築
* python
    * 3.12.2で実行確認しているがおそらくLinux or Macに標準搭載されているPython3で実行可能
* clang-format
    * 各sourceを出力するときに使用
    * 以下の方法でインストール可能
        * linux `sudo apt install clang-format`
        * mac `brew install clang-format`

## 使用方法
* 以下のコマンドを実行してスクリプトを使用します：
```sh
python3 auto-compile-exec.py [target_dir] [input_dir] [--nooutput]
```
* 引数
    * target_dir：Cソースファイルが含まれるディレクトリのパス。
    * input_dir：オプション。入力ファイルが含まれるディレクトリのパス。
    * --nooutput：オプション。コンパイル結果をテキストファイルに出力しない場合に指定します。

### 使用例
* repository内のexampleで動作確認可能
    * git clone していればrepository rootで以下を実行可能
    * `chmod +x auto-compile-exec.py` すると`python *.py`しなくて動く
1. ソースファイルのみをコンパイルし、結果を表示
    * `./auto-compile-exec.py ./example/no_input/code01/` 
2. ソースファイルをコンパイルし、指定された入力ファイルを使用して実行
    * `./auto-compile-exec.py ./example/with_input/code02/ ./example/with_input/in/`
3. 結果をmarkdownに出力せずにコンパイルおよび実行
    * `./auto-compile-exec.py ./example/no_input/code01/ --nooutput`
    * `./auto-compile-exec.py ./example/with_input/code02/ ./example/with_input/in/ --nooutput`

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
### コード出力
* print_source関数の`subprocess.run`部分を変更することで出力されるコードを変更
    * デフォルト実装では見やすいようにformatをかけている
    * 何かしらの事情で`clang-format`をインストールできない場合は`display_command`を`cat`に変更
```python
def print_source(file_path: os.path):
    #display_command = "clang-format"
    #↑を↓に変更
    display_command = "cat"
    display_command_result: subprocess.CompletedProcess = subprocess.run(
        [display_command, file_path], capture_output=True, text=True
    )
```

### コンパイル対象ファイル
* auto_compile_exec関数内の`target_file_list = filter()`を変更することでループを回す対象を変更可能
* `.c`ではなく`.cpp`に変更する場合は以下のように変更
```python
def auto_compile_exec(
    target_dir: os.path,
    compile_timeout: int,
    execution_timeout: int,
    input_dir=None,
):
    # 省略

    # 対象ファイルを変えたい場合はこの部分を変更
    #target_file_list = filter(lambda file: file.endswith(".c"), os.listdir(target_dir))
    target_file_list = filter(lambda file: file.endswith(".cpp"), os.listdir(target_dir))
```

### コンパイルコマンド
* auto_compile_exec関数内の`compile_command = []`を変更することでコンパイル方法を変更可能
* `gcc`ではなく`g++`に変更する場合は以下のように変更
```python
def auto_compile_exec(
    target_dir: os.path,
    compile_timeout: int,
    execution_timeout: int,
    input_dir=None,
):
    # 省略

    filepath_after_compile, _ = os.path.splitext(file_path)
    # コンパイルコマンドを変更したい場合この部分を修正
    #compile_command = ["gcc", file_path, "-o", filepath_after_compile]
    compile_command = ["g++", file_path, "-o", filepath_after_compile]
```