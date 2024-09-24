#!/usr/bin/env python3
from pathlib import Path
import subprocess
import argparse
import sys
import traceback
import re
# 各種タイムアウト時間を設定
COMPILE_TIMEOUT = 4
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
    """
    strip_language = "" if language is None else language.strip()
    strip_file_name = "" if file_name is None else f":{file_name}"
    file_with_language = strip_language + strip_file_name
    print(f"```{file_with_language}\n{code.strip()}\n```")


# コード出力の部分を変更したい場合この関数を変更
def print_source(file_path: Path):
    """
    指定されたファイルの内容をコードブロックとして出力します。clang-format を使用して整形します。

    Parameters:
    file_path (Path): ソースファイルのパス。
    """
    display_command = "clang-format"
    display_command_result: subprocess.CompletedProcess = subprocess.run(
        [display_command, file_path], capture_output=True, text=True
    )
    print_codeblock(display_command_result.stdout, "c")


def execution(executable_file_path: Path, execution_timeout: int, infile = None, outfile = None):
    """
    指定された実行可能ファイルを実行し、結果をコードブロックとして出力します。

    Parameters:
    executable_file_path (Path): 実行可能ファイルのパス。
    execution_timeout (int): 実行タイムアウトの秒数。
    infile (file object, optional): 標準入力として使用するファイルオブジェクト。デフォルトは None。
    """
    infile = subprocess.PIPE if infile is None else infile
    outfile = subprocess.PIPE if infile is None else outfile
    exe_result: subprocess.CompletedProcess = subprocess.run(
        [executable_file_path],
        stdin=infile,
        stdout=outfile,  
        text=True,
        timeout=execution_timeout,
    )


def auto_compile_exec(
    target_dir: Path,
    compile_timeout: int,
    execution_timeout: int,
    input_dir=None,
):
    """
    指定されたディレクトリ内のCソースファイルをコンパイルし、実行結果を出力します。

    Parameters:
    target_dir (Path): コンパイル対象のソースファイルが含まれるディレクトリのパス。
    compile_timeout (int): コンパイルタイムアウトの秒数。
    execution_timeout (int): 実行タイムアウトの秒数。
    input_dir (Path, optional): 入力ファイルが含まれるディレクトリのパス。デフォルトは None。
    """
    # 対象ディレクトリのパスを正規化
    target_dir = target_dir.resolve()
    print(f"# {target_dir.name}")

    # 対象ファイルのリストを取得
    target_file_list = [file for file in target_dir.iterdir() if file.suffix == ".c"]

    # ディレクトリ内のファイルに対してループ処理を行う
    before_file_list = set(target_dir.iterdir())
    print_source_error = False

    for file in sorted(target_file_list):
        print(f"## {file.name}")

        print("### source file")
        try:
            print_source(file)
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

        filepath_after_compile = file.with_suffix("")
        # コンパイルコマンドを変更したい場合この部分を修正
        compile_command = ["gcc", file, "-o", filepath_after_compile]
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
            print(f"コンパイルが{compile_timeout}秒を超えたため強制終了しました")
            continue

        print("### 実行結果")
        if input_dir is None:
            # 入力ファイルが無い場合
            try:
                execution(filepath_after_compile, execution_timeout)
            except subprocess.TimeoutExpired:
                print(f"* 実行時間が{execution_timeout}秒を超えたため強制終了しました")
                continue
        else:
            # 各入力ファイルに対してプログラムを実行
            input_files = sorted(
                [f for f in Path(input_dir).iterdir() if f.suffix == ".txt"]
            )
            for input_file in input_files:
                input_file_name = input_file.name
                print(f"#### 入力-{input_file_name}")
                with input_file.open("r") as infile:
                    print_codeblock(infile.read(), "txt", input_file_name)
                print("#### 出力")
                with input_file.open("r") as infile:
                    try:
                        execution(filepath_after_compile, execution_timeout, infile)
                    except subprocess.TimeoutExpired:
                        print(
                            f"* 実行時間が{execution_timeout}秒を超えたため強制終了しました"
                        )
                        break
    after_file_list = set(target_dir.iterdir())
    print("## 削除ファイル")
    for file in after_file_list.difference(before_file_list):
        file.unlink()
        print(f"* {file}")
    if print_source_error:
        exit(1)

def pair_input_output(directory) -> list[tuple[Path, Path]]:
    # ディレクトリをPathオブジェクトに変換
    dir_path = Path(directory)
    
    # 正規表現でinとoutファイルを識別
    input_files = sorted([f for f in dir_path.glob('in*.txt') if re.match(r'in\d+\.txt', f.name)])
    output_files = sorted([f for f in dir_path.glob('out*.txt') if re.match(r'out\d+\.txt', f.name)])

    # ファイル番号を抽出して辞書に変換
    input_dict = {int(re.search(r'\d+', f.name).group()): f for f in input_files}
    output_dict = {int(re.search(r'\d+', f.name).group()): f for f in output_files}

    # タプルで(inのパス, outのパス)のペアを作成
    pairs = []
    for num, in_file in input_dict.items():
        if num in output_dict:
            pairs.append((in_file, output_dict[num]))
        else:
            # エラー 後で書く
            exit(45)
    
    return pairs

def gcc_compile(target_dir : Path, 
                compile_timeout: int,
    execution_timeout: int,
    intput_output_dir : Path):
    c_files = list(target_dir.rglob('*.c'))
    print_source_error = False
    for file in sorted(c_files):
        print(f"## {file.name}")
        print("### source file")
        try:
            print_source(file)
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
            
        filepath_after_compile = file.with_suffix("")
        compile_command = ["gcc", file, "-o", filepath_after_compile]
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
            print(f"コンパイルが{compile_timeout}秒を超えたため強制終了しました")
            continue        
        
        print("### 実行結果")
        if intput_output_dir:
            intput_output_pair_list = pair_input_output(intput_output_dir)
            for input_file, expected_file in intput_output_pair_list:
                print(f"#### 入力-{input_file.name}")
                with input_file.open("r") as infile:
                    print_codeblock(infile.read(), "txt", input_file)
                print("#### 出力")
                output_file_path = filepath_after_compile.with_suffix(".txt")
                with input_file.open("r") as infile:
                    with output_file_path.open("w") as outfile:
                        try:
                            execution(filepath_after_compile, execution_timeout, infile, outfile)
                        except subprocess.TimeoutExpired:
                            print(
                                f"* 実行時間が{execution_timeout}秒を超えたため強制終了しました"
                            )
                            break
                                    
                with output_file_path.open("r") as outfile:  
                    print_codeblock(outfile.read())
                print("#### diff")
                diff_result = subprocess.run(
                    ["diff", "-wB", expected_file , output_file_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
                if diff_result.returncode == 0:
                    print("* ok")
                else:
                    print("* NG")
                    print_codeblock(diff_result.stdout)
                output_file_path.unlink()
        else:
            # 入力ファイルが無い場合
            try:
                execution(filepath_after_compile, execution_timeout)
            except subprocess.TimeoutExpired:
                print(f"* 実行時間が{execution_timeout}秒を超えたため強制終了しました")
                continue            
    if print_source_error:
        exit(1)
        
        
    

def main():
    parser = argparse.ArgumentParser(
        description="This script will compile all the source code in the folder."
    )
    parser.add_argument(
        "target_dir", help="The path to the folder containing the source code."
    )
    parser.add_argument(
        "-io",
        "--input_output",
        type=Path,
        default=None
    )


    args = parser.parse_args()
    
    target_dir = Path(args.target_dir)
    input_output_dir = Path(args.input_output) if args.input_output else None
    
    gcc_compile(target_dir, COMPILE_TIMEOUT, EXECUTION_TIMEOUT, input_output_dir)

    return
    if args.nooutput:
        auto_compile_exec(
            target_dir,
            COMPILE_TIMEOUT,
            EXECUTION_TIMEOUT,
            input_dir,
        )
    else:
        dir_name = target_dir.resolve().name
        output_file = Path.cwd() / f"{dir_name}_out.md"
        with output_file.open("w") as outfile:
            dual_output = DualOutput(sys.stdout, outfile)
            sys.stdout = dual_output
            sys.stderr = dual_output
            try:
                auto_compile_exec(
                    target_dir, COMPILE_TIMEOUT, EXECUTION_TIMEOUT, input_dir
                )
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__


if __name__ == "__main__":
    main()
