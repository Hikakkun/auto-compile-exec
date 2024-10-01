#!/usr/bin/env python3
from pathlib import Path
import argparse
import configparser
import json
from functools import reduce
import subprocess
import re
import pprint
import sys
COMPILE_TIMEOUT = 4
EXECUTION_TIMEOUT = 2

def get_student_list_from_config_ini(config_file : Path) -> list[str] | None:
    """
    config.iniファイルから学生のリストを取得します。

    Parameters:
        config_file (Path): config.iniファイルのパス。

    Returns:
        list[str] | None: 学生番号のリスト。取得できない場合はNone。
    """
    student_list = None
    config_ini = configparser.ConfigParser()
    try:
        config_ini.read(config_file, encoding='utf-8')
        student_list_str = config_ini.get("DEFAULT", "StudentList")
        student_list = json.loads(student_list_str)    
    except Exception as _:
        student_list = None    
    finally:
        return student_list

def is_eight_digit_number(s : str):
    return s.isdigit() and len(s) == 8


def parse_student_number(student_number_str : str) -> list[str] | None:
    student_list = student_number_str.split("|")
    if reduce(lambda x, y: x and is_eight_digit_number(y), student_list, True):
        return student_list
    else:
        return None

def convert_dict_from_target_dir(target_dir: Path):
    source_files = target_dir.glob("*.c")
    return {path.stem : path for path in source_files}

def get_soruce(path : Path, command : str = "clang-format"):
    result = subprocess.run(
        [command, path],
        capture_output=True, 
        text=True
    )
    return f"//{str(path)}" + "\n" + result.stdout

def include_source_compile(include_dir : Path | None) -> list[Path]:
    if include_dir is None:
        return []
    compile_target_files = include_dir.glob("*.c")
    compiled_files : list[Path] = []
    for compile_target_file in compile_target_files:
        compiled_file = compile_target_file.with_suffix("")
        subprocess.run(
            ["gcc", "-c", compile_target_file, "-o", compiled_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )       
        compiled_files.append(compiled_file)
    return compiled_files

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

def get_runtime_error_info(error_code : int) -> str:
    match error_code:
        case -6:
            return f"returncode={-6},abort"
        case -7:
            return f"returncode={-7},bus error"
        case -8:
            return f"returncode={-8},floating point exception"
        case -11:
            return f"returncode={-11},segmentation fault"
        case _:
            return f"returncode={error_code},segmentation fault"

def run_program(
    executable_path: Path,
    execution_timeout: int,
    nodiff: bool,
    input_file: Path | None = None,
    expected_file: Path | None = None
) -> dict:
    """
    コンパイルされたプログラムを実行し、実行結果を収集します。

    Parameters:
        executable_path (Path): 実行可能ファイルのパス。
        execution_timeout (int): プログラムの実行タイムアウト時間（秒）。
        nodiff (bool): 出力の差分チェックを行わない場合はTrue。
        input_file (Path | None): 入力ファイルのパス（ない場合はNone）。
        expected_file (Path | None): 期待される出力ファイルのパス（ない場合はNone）。

    Returns:
        dict: 実行結果を含む辞書。
    """
    runtime_error = None
    output = None
    input_txt = None
    expected_txt = None
    diff = None

    if input_file:
        # 入力ファイルと期待される出力を読み込み
        input_txt = input_file.read_text()
        if expected_file:
            expected_txt = expected_file.read_text()
        # 一時的な出力ファイルを作成
        output_file_path = executable_path.with_suffix(".txt")
        with (
            input_file.open("r") as infile,
            output_file_path.open("w") as outfile
        ):
            try:
                exe_result = subprocess.run(
                    [executable_path],
                    stdin=infile,
                    stdout=outfile,
                    text=True,
                    timeout=execution_timeout,
                )
                exe_result.check_returncode()
            except subprocess.CalledProcessError:
                runtime_error = get_runtime_error_info(exe_result.returncode)
            except subprocess.TimeoutExpired:
                runtime_error = "timeout"
            else:
                if not nodiff and expected_file:
                    diff_result = subprocess.run(
                        ["diff", "-wB", expected_file, output_file_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if diff_result.returncode != 0:
                        diff = diff_result.stdout
            # 出力ファイルから出力を読み込み
            output = output_file_path.read_text()
            # 一時ファイルを削除
            output_file_path.unlink()
    else:
        try:
            exe_result = subprocess.run(
                [executable_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=execution_timeout,
            )
            exe_result.check_returncode()
            output = exe_result.stdout
        except subprocess.CalledProcessError:
            runtime_error = get_runtime_error_info(exe_result.returncode)
        except subprocess.TimeoutExpired:
            runtime_error = "timeout"

    # 実行結果の辞書を作成
    execution_result_dict = {
        "in" : input_txt,
        "out": output,
        "expected" : expected_txt,
        "diff" : diff,
        "runtime_error": runtime_error,
    }
    return execution_result_dict


def auto_compile_exec(
    target_dir_list: list[Path],
    compile_timeout: int,
    execution_timeout: int,
    intput_output_dir: Path | None,
    include_dir: Path | None,
    nodiff: bool,
    student_list: list[str] | None,
    uninitialized_errpr : bool,
):
    target_dir_dict_list = list(map(convert_dict_from_target_dir, target_dir_list))
    target_dir_dict = target_dir_dict_list.pop(0)
    compiled_files = include_source_compile(include_dir)
    intput_output_pair_list: list[tuple[Path, Path]] | None = pair_input_output(intput_output_dir) if intput_output_dir else None
    student_number_set : set[str] = set(map(str, student_list))
    output_json = {}
    for student_number in sorted(target_dir_dict):
        if student_number not in student_number_set:
            continue
        data = dict()
        path = target_dir_dict[student_number]
        other_paths = list(map(lambda dct: dct.get(student_number, None), target_dir_dict_list))
        path_list: list[Path] = [path, *other_paths]
        source_list: list[str] = [get_soruce(source_path) for source_path in path_list]
        filepath_after_compile = path.with_suffix("")
        compile_command = [
            "gcc",
            "-o",
            filepath_after_compile,
            *path_list,
            "-lm",
        ]
        if uninitialized_errpr:
            compile_command.extend(["-Wall", "-Wuninitialized", "-Werror"])
            
        if include_dir:
            compile_command.extend(["-I", include_dir])
            compile_command.extend(compiled_files)
        execution_result_list = []
        compile_error = None
        data["source"] = source_list
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
            compile_error = compile_result.stderr
        except subprocess.TimeoutExpired:
            compile_error = "timeout"
        else:
            if intput_output_pair_list:
                for input_file, expected_file in intput_output_pair_list:
                    execution_result_dict = run_program(
                        executable_path=filepath_after_compile,
                        execution_timeout=execution_timeout,
                        nodiff=nodiff,
                        input_file=input_file,
                        expected_file=expected_file,
                    )
                    execution_result_list.append(execution_result_dict)
            else:
                execution_result_dict = run_program(
                    executable_path=filepath_after_compile,
                    execution_timeout=execution_timeout,
                    nodiff=nodiff,
                )
                execution_result_list.append(execution_result_dict)
        data["compile_error"] = compile_error
        data["execution"] = execution_result_list
        output_json[student_number] = data
        pprinter = pprint.PrettyPrinter(stream=sys.stderr)
        pprinter.pprint(data)
        if filepath_after_compile.exists() and filepath_after_compile.is_file():
            filepath_after_compile.unlink()
    for compiled_file in compiled_files:
        compiled_file.unlink()
    
    return json.dumps(output_json, indent=4)
    
def main():
    parser = argparse.ArgumentParser(
        description="学生のプログラムを自動でコンパイルし、テストを実行するスクリプトです。指定したディレクトリ内のCソースコードをコンパイルし、必要に応じて入出力ファイルを用いた実行を行い、結果を収集します。"
    )
    parser.add_argument(
        "target_dir",
        help="ソースコードが含まれるディレクトリのパスを1つ以上指定してください。",
        nargs="+"
    )
    parser.add_argument(
        "-io",
        "--input_output",
        help="入出力テストデータ（入力ファイルと期待される出力ファイル）が含まれるディレクトリのパス。",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "-I",
        "--include",
        help="事前に準備されたCファイルを含むディレクトリのパス。",
        type=Path,
        default=None,
    )

    parser.add_argument(
        "-sn",
        "--student_number",
        help="学生番号をパイプ(|)区切りで指定します。指定しない場合はconfig.iniから読み取ります。",
        type=str,
        default=None
    )
    parser.add_argument(
        "--nodiff",
        help="出力の差分チェックをスキップする場合に使用します。",
        action="store_true"
    )
    parser.add_argument(
        "--output_markdown",
        help="コンパイル結果をテキストファイルに出力しない場合に使用します。",
        action="store_true",
    )
    parser.add_argument(
        "--uninitialized_error",
        help="未初期化変数に関するエラーを強制するためのオプションです。",
        action="store_true",
    )

    args = parser.parse_args()
    target_dir_list = list(map(lambda fila_path : Path(fila_path), args.target_dir))
    input_output_dir = Path(args.input_output) if args.input_output else None
    include_dir = Path(args.include) if args.include else None
    if args.student_number is None:
        student_list = get_student_list_from_config_ini(Path("config.ini"))
    else:
        student_list = parse_student_number(args.student_number) 
    json_str = auto_compile_exec(
        target_dir_list=target_dir_list,
        compile_timeout=COMPILE_TIMEOUT,
        execution_timeout=EXECUTION_TIMEOUT,
        intput_output_dir=input_output_dir,
        include_dir=include_dir,
        nodiff=args.nodiff,
        student_list=student_list,
        uninitialized_errpr=args.uninitialized_error
    )
    
    if args.output_markdown:
        from convert_md import convert_md
        convert_md(json_str)
    else:
        print(json_str)

if __name__ == "__main__":
    main()
