#!/usr/bin/env python3
import os
import subprocess
import argparse
import sys
import traceback

COMPILE_TIMEOTU = 2
EXECUTION_TIMEOUT = 2


class DualOutput:
    """
    複数の出力ストリームに同時に書き込むためのユーティリティクラス。

    このクラスは、指定された複数の出力ストリーム（例：ファイル、標準出力）に対して
    同時にメッセージを書き込むための機能を提供します。

    Attributes:
    outputs (tuple): 書き込み先の出力ストリームのタプル。
    """
    def __init__(self, *outputs):
        """
        DualOutputクラスのコンストラクタ。

        Parameters:
        outputs (*): 書き込み先の出力ストリーム。可変長引数として指定します。
        """
        self.outputs = outputs

    def write(self, message):
        """
        指定されたメッセージをすべての出力ストリームに書き込みます。

        Parameters:
        message (str): 書き込むメッセージ。
        """
        for output in self.outputs:
            output.write(message)

    def flush(self):
        """
        すべての出力ストリームをフラッシュします。

        フラッシュは、バッファに溜まったデータを実際の出力先に書き出す操作です。
        """
        for output in self.outputs:
            output.flush()


def print_codeblock(code: str, language: str = None, file_name: str = None):
    """
    指定されたコードを適切なコードブロック形式で出力します。

    Parameters:
    code (str): 出力するコードの内容。
    language (str, optional): コードの言語。デフォルトは None。
    file_name (str, optional): コードが含まれるファイルの名前。デフォルトは None。

    Returns:
    None
    """
    file_with_language = f"{"" if language is None else language.strip()}{"" if file_name is None else ":"+file_name.strip()}"
    print(f"```{file_with_language}\n{code.strip()}\n```")

#コード出力の部分を変更したい場合この関数を変更
def print_source(file_path: os.path):
    """
    指定されたファイルの内容をコードブロックとして出力します。clang-format を使用して整形します。

    Parameters:
    file_path (os.path): ソースファイルのパス。

    Returns:
    None
    """
    display_command = "clang-format"
    display_command_result: subprocess.CompletedProcess = subprocess.run(
        [display_command, file_path], capture_output=True, text=True
    )
    print_codeblock(display_command_result.stdout, "c")


def execution(executable_file_path: os.path, execution_timeout: int, infile=None):
    """
    指定された実行可能ファイルを実行し、結果をコードブロックとして出力します。

    Parameters:
    executable_file_path (os.path): 実行可能ファイルのパス。
    execution_timeout (int): 実行タイムアウトの秒数。
    infile (file object, optional): 標準入力として使用するファイルオブジェクト。デフォルトは None。

    Returns:
    None
    """
    exe_result: subprocess.CompletedProcess = subprocess.run(
        [executable_file_path],
        stdin=infile,
        capture_output=True,
        text=True,
        timeout=execution_timeout,
    )
    print_codeblock(exe_result.stdout, "txt")


def auto_compile_exec(
    target_dir: os.path,
    compile_timeout: int,
    execution_timeout: int,
    input_dir=None,
    output=True,
):
    """
    指定されたディレクトリ内のCソースファイルをコンパイルし、実行結果を出力します。

    Parameters:
    target_dir (os.path): Cソースファイルが含まれるディレクトリのパス。
    compile_timeout (int): コンパイルタイムアウトの秒数。
    execution_timeout (int): 実行タイムアウトの秒数。
    input_dir (os.path, optional): 入力ファイルが含まれるディレクトリのパス。デフォルトは None。
    output (bool, optional): コンパイル結果をコマンドラインに出力するかどうか。デフォルトは True。

    Returns:
    None
    """
    # 第一引数の対象ディレクトリの末尾に/があれば削除
    if target_dir.endswith("/"):
        target_dir = target_dir[:-1]
    print(f"# {os.path.basename(target_dir)}")
    # ディレクトリ内のファイルに対してループ処理を行う
    before_file_list = set(os.listdir(target_dir))
    print_source_error = False
    for file in sorted(os.listdir(target_dir)):
        if file.endswith(".c"):
            file_path = os.path.join(target_dir, file)
            filepath_after_compile = file_path[:-2]  # 拡張子を除いたファイル名
            compile_command = ["gcc", file_path, "-o", filepath_after_compile]
            print(f"## {os.path.basename(file_path)}")

            print("### source file")
            try:
                print_source(file_path)
            except FileNotFoundError:
                print(traceback.format_exc())
                print(
                    "There is a problem with the arguments of the subprocess.run function in the print_source function."
                )
                print("Please check the following:")
                print("* Is the command correct?")
                print("* Is the command path correct?")
                print_source_error = True
                break
            try:
                compile_result = subprocess.run(
                    compile_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=compile_timeout,
                )
                compile_result.check_returncode()
            except subprocess.CalledProcessError:
                print("### compile error")
                print_codeblock(compile_result.stderr, "bash")
                continue
            except subprocess.TimeoutExpired:
                print("### compile timeout")
                print(f"コンパイルが{compile_timeout}secを超えたため強制終了しました")

            print("### 実行結果")
            if input_dir is None:
                # 入力ファイルが無い場合
                try:
                    execution(filepath_after_compile, execution_timeout)
                except subprocess.TimeoutExpired:
                    print(
                        f"* 実行時間が{execution_timeout}secを超えたため強制終了しました"
                    )
                    continue

            else:
                # 各入力ファイルに対してプログラムを実行
                input_files = sorted(
                    [f for f in os.listdir(input_dir) if f.endswith(".txt")]
                )
                for input_file in input_files:
                    input_file_path = os.path.join(input_dir, input_file)
                    input_file_name = os.path.basename(input_file)
                    print(f"#### 入力-{input_file_name}")
                    with open(input_file_path, "r") as infile:
                        print_codeblock(infile.read(), "txt", input_file_name)
                    print("#### 出力")
                    with open(input_file_path, "r") as infile:
                        try:
                            execution(filepath_after_compile, execution_timeout, infile)
                        except subprocess.TimeoutExpired:
                            print(
                                f"* 実行時間が{execution_timeout}secを超えたため強制終了しました"
                            )
                            break
    after_file_list = set(os.listdir(target_dir))
    print("## 削除ファイル")
    for file in after_file_list.difference(before_file_list):
        remove_file_path = os.path.join(target_dir, file)
        os.remove(remove_file_path)
        print(f"* {remove_file_path}")
    if print_source_error:
        exit(1)


def main():
    """
    スクリプトのエントリーポイント。引数を解析し、自動コンパイルと実行を開始します。

    Parameters:
    None

    Returns:
    None
    """
    parser = argparse.ArgumentParser(
        description="This script will compile all the source code in the folder."
    )
    parser.add_argument(
        "target_dir", help="The path to the folder containing the source code."
    )
    parser.add_argument(
        "input_dir",
        nargs="?",
        default=None,
        help="The path to the folder containing the input .txt files.",
    )
    parser.add_argument(
        "--nooutput",
        action="store_true",
        help="Do not output compilation results to a text file.",
    )

    args = parser.parse_args()
    if args.nooutput:
        auto_compile_exec(
            args.target_dir,
            COMPILE_TIMEOTU,
            EXECUTION_TIMEOUT,
            args.input_dir,
            output=False,
        )
    else:
        dir_name = os.path.basename(os.path.normpath(args.target_dir))
        with open(os.path.join(os.getcwd(), f"{dir_name}_out.md"), "w") as outfile:
            dual_output = DualOutput(sys.stdout, outfile)
            sys.stdout = dual_output
            sys.stderr = dual_output
            try:
                auto_compile_exec(
                    args.target_dir, COMPILE_TIMEOTU, EXECUTION_TIMEOUT, args.input_dir
                )
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__


if __name__ == "__main__":
    main()
