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
COMPILE_TIMEOTU = 2
EXECUTION_TIMEOUT = 2
```
### コード出力
* print_source関数のsubprocess.run部分を変更することで出力されるコードを変更
    * デフォルト実装では見やすいようにformatをかけている
    * 何かしらの事情で`clang-format`をインストールできない場合は`displau_command`を`cat`に変更
```python
def print_source(file_path: os.path):
    #displau_command = "clang-format"
    #↑を↓に変更
    displau_command = "cat"
    display_command_result: subprocess.CompletedProcess = subprocess.run(
        [displau_command, file_path], capture_output=True, text=True
    )
    print_codeblock(display_command_result.stdout, "c")

```