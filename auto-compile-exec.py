#!/usr/bin/env python3
from pathlib import Path
import subprocess
import argparse
import sys
import re
import configparser
import json
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
def print_source(file_path: Path, display_command : str = "clang-format"):
    """
    指定されたファイルの内容をコードブロックとして出力します。clang-format を使用して整形します。

    Parameters:
    file_path (Path): ソースファイルのパス。
    """
    display_command_result: subprocess.CompletedProcess = subprocess.run(
        [display_command, file_path], capture_output=True, text=True
    )
    print_codeblock(display_command_result.stdout, "c", file_path)

def print_runtime_error(error_code : int):
    match error_code:
        case -6:
            print("* abort")
            print("* abort()関数が呼ばれたとき。プログラムが異常終了する場合など")
        case -7:
            print("* Bus error")
            print("* メモリアラインメントが不正です（例: 整数が奇数アドレスに置かれるなど）")
        case -8:
            print("* Floating point exception")
            print("*  0での除算や不正な浮動小数点演算が行われました")
        case -11:
            print("* Segmentation fault")
            print("* 無効なメモリアクセスが行われました(配列の範囲外アクセス、NULLポインタへのアクセス)")
        case _:
            print(f"* return_code = {error_code}")
def pair_input_output(directory) -> list[tuple[Path, Path]]:
    """
    指定されたディレクトリ内の入力ファイルと対応する出力ファイルのペアを取得します。

    この関数は、ファイル名に基づいてinファイルとoutファイルをペアにして返します。

    Parameters:
        directory (str): 入力および出力ファイルが含まれるディレクトリのパス。

    Returns:
        list[tuple[Path, Path]]: 対応する入力ファイルと出力ファイルのペアのリスト。
    """
    # ディレクトリをPathオブジェクトに変換
    dir_path = Path(directory)

    # 正規表現でinとoutファイルを識別
    input_files = sorted(
        [f for f in dir_path.glob("in*.txt") if re.match(r"in\d+\.txt", f.name)]
    )
    output_files = sorted(
        [f for f in dir_path.glob("out*.txt") if re.match(r"out\d+\.txt", f.name)]
    )

    # ファイル番号を抽出して辞書に変換
    input_dict = {int(re.search(r"\d+", f.name).group()): f for f in input_files}
    output_dict = {int(re.search(r"\d+", f.name).group()): f for f in output_files}

    # タプルで(inのパス, outのパス)のペアを作成
    pairs = []
    for num, in_file in input_dict.items():
        if num in output_dict:
            pairs.append((in_file, output_dict[num]))
        else:
            # エラー 後で書く
            exit(45)

    return pairs


def auto_compile_exec(
    target_dir: Path,
    compile_timeout: int,
    execution_timeout: int,
    intput_output_dir: Path | None = None,
    header_dir: Path | None = None,
):
    """
    指定されたディレクトリ内のCファイルをコンパイルし、結果を実行します。

    コンパイルエラーやタイムアウトが発生した場合、その詳細を出力します。
    実行後、指定された入力と期待される出力を比較し、差分を表示します。

    Parameters:
        target_dir (Path): Cファイルが含まれるディレクトリのパス。
        compile_timeout (int): コンパイルのタイムアウト時間（秒）。
        execution_timeout (int): 実行のタイムアウト時間（秒）。
        intput_output_dir (Path, optional): 入力ファイルと出力ファイルが含まれるディレクトリのパス。デフォルトは None。
        header_dir (Path, optional): ヘッダファイルが含まれるディレクトリのパス。デフォルトは None。
    """
    # TAが用意するソースコードを事前コンパイル
    c_compiled_files :list[Path] = []
    if header_dir:
        c_compile_files = list(header_dir.glob("*.c"))
        for c_file in c_compile_files:
            c_compiled_file = c_file.with_suffix("")
            try:
                compile_result = subprocess.run(
                    ["gcc", "-c", c_file, "-o", c_compiled_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                compile_result.check_returncode()
            except Exception as e:
                print("# 事前に用意したファイルのエラー")
                print(f"* `{" ".join(map(str, compile_result.args))}`")
                print_codeblock(compile_result.stderr, "bash")
                for compiled in c_compiled_files:
                    compiled.unlink()
                exit(1)    
            c_compiled_files.append(c_compiled_file)
    
    config_file = Path('config.ini')
    student_list = None
    config_ini = configparser.ConfigParser()
    try:
        config_ini.read(config_file, encoding='utf-8')
        try:
            student_list_str = config_ini.get("DEFAULT", "StudentList")
            student_list = json.loads(student_list_str)
        except configparser.NoOptionError as no_option_error:
            if config_file.exists():
                print("""* config.ini は存在していますが `config_ini.get("DEFAULT", "StudentList")`の値がありません""")
                
    except configparser.ParsingError as parsing_error:
        print("* config.ini をパースできません")
        print_codeblock(str(parsing_error), "bash")
    
    c_files : list[Path] = list(target_dir.rglob("*.c"))
    if student_list is None:
        target_file_list = sorted(c_files)
    else:
        student_set = {student_number for student_number in map(str, student_list)}
        print(f"* `{student_set=}`")
        target_file_list = sorted(list(filter(lambda file : file.stem in student_set, c_files)))
        

    for file in target_file_list:
        print(f"## {file.name}")
        print("### source file")
        #提出されたソースコードを表示
        try:
            print_source(file)
        except FileNotFoundError:
            # clang-formater が見つからない場合 cat を使用
            print_source(file, "cat")

        filepath_after_compile = file.with_suffix("")
        if header_dir is None:
            compile_command = ["gcc", file, "-o", filepath_after_compile]
        else:                
            compile_command = [
                "gcc",
                "-I",
                header_dir,
                "-o",
                filepath_after_compile,
                file,
                *c_compiled_files,
            ]

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
                print_codeblock(input_file.read_text(), "txt", input_file)
                output_file_path = filepath_after_compile.with_suffix(".txt")
                with (
                    input_file.open("r") as infile,
                    output_file_path.open("w") as outfile
                ):
                    try:
                        exe_result = subprocess.run(
                            [filepath_after_compile],
                            stdin=infile,
                            stdout=outfile,
                            text=True,
                            timeout=execution_timeout,
                        )
                        exe_result.check_returncode()
                    except subprocess.CalledProcessError:
                        print("#### Runtime error")
                        print_runtime_error(exe_result.returncode)
                    except subprocess.TimeoutExpired:
                        print(
                            f"* 実行時間が{execution_timeout}秒を超えたため強制終了しました"
                        )
                        break
                    else:
                        print("##### 出力")
                        print_codeblock(output_file_path.read_text())
                        print("##### diff")
                        diff_result = subprocess.run(
                            ["diff", "-wB", expected_file, output_file_path],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                        )

                        if diff_result.returncode == 0:
                            print("* ok")
                        else:
                            print("* NG")
                            print_codeblock(diff_result.stdout)
                    finally:
                        output_file_path.unlink()
            filepath_after_compile.unlink()
        else:
            # 入力ファイルが無い場合
            try:
                exe_result = subprocess.run(
                    [filepath_after_compile],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=execution_timeout,
                )
                exe_result.check_returncode()
                print("#### 出力")
                print_codeblock(exe_result.stdout ,"txt")
            except subprocess.CalledProcessError:
                print("#### Runtime error")
                print_runtime_error(exe_result.returncode)
                continue                                
            except subprocess.TimeoutExpired:
                print(f"* 実行時間が{execution_timeout}秒を超えたため強制終了しました")
                continue
            finally:
                filepath_after_compile.unlink()
    for compiled_file in c_compiled_files:
        compiled_file.unlink()
        

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
        help="Path to the directory containing input and expected output text files.",
        type=Path,
        default=None,
    )

    parser.add_argument(
        "-H",
        "--header",
        help="A directory containing pre-prepared c files",
        type=Path,
        default=None,
    )

    parser.add_argument(
        "--nooutput",
        action="store_true",
        help="Do not output compilation results to a text file.",
    )

    args = parser.parse_args()

    target_dir = Path(args.target_dir)
    input_output_dir = Path(args.input_output) if args.input_output else None
    header_dir = Path(args.header) if args.header else None

    if args.nooutput:
        auto_compile_exec(
            target_dir, COMPILE_TIMEOUT, EXECUTION_TIMEOUT, input_output_dir, header_dir
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
                    target_dir,
                    COMPILE_TIMEOUT,
                    EXECUTION_TIMEOUT,
                    input_output_dir,
                    header_dir,
                )
            finally:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__


if __name__ == "__main__":
    main()
