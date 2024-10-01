#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import sys


def print_codeblock(code: str, language: str = None, file_name: str = None):
    """
    指定されたコードをコードブロック形式で出力します。

    Parameters:
    code (str): 出力するコードの内容。
    language (str, optional): コードの言語。デフォルトは None。
    file_name (str, optional): コードが含まれるファイルの名前。デフォルトは None。
    """
    strip_language = "" if language is None else language.strip()
    strip_file_name = "" if file_name is None else f":{file_name}"
    file_with_language = strip_language + strip_file_name
    print(f"```{file_with_language}\n{code.strip()}\n```")


def print_execution(dct: dict[str, str], key: str, languagea: str):
    """
    辞書から指定されたキーの値を取得し、それをコードブロック形式で出力します。

    Parameters:
    dct (dict[str, str]): 実行情報を含む辞書。
    key (str): 出力する内容のキー。辞書内の特定の情報を指定します（例: "runtime_error"、"diff"など）。
    language (str): コードの言語。コードブロックのシンタックスハイライト用。

    Note:
    指定されたキーが辞書内に存在し、かつその値が空でない場合に、その内容をコードブロックとして出力します。
    """
    if key in dct and dct[key]:
        print(f"#### {key}")
        print_codeblock(dct[key])


def convert_md(json_str: str, file_name: str = "out.md"):
    """
    JSON形式の文字列をMarkdown形式に変換し、出力します。

    Parameters:
    json_str (str): 学生の情報を含むJSON形式の文字列。
    file_name (str, optional): Markdown出力のファイル名として使用される文字列。デフォルトは "out.md"。

    Note:
    JSONデータから各学生の情報を取得し、コード、コンパイルエラー、実行結果をMarkdown形式で出力します。
    - 学生ごとに見出しを作成し、ソースコード、コンパイルエラー、実行結果を適切な形式で出力します。
    - 実行結果には入力、出力、期待結果などが含まれます。
    """
    print(f"# {file_name}")
    data = json.loads(json_str)
    for student_number, info in data.items():
        print(f"## {student_number}")
        print("### code")
        for source in info["source"]:
            print_codeblock(source, "c")
        compile_error = info["compile_error"]
        if compile_error is not None:
            print("### compile error")
            print_codeblock(compile_error, "bash")
        # print(f"")
        execution_list = info["execution"]
        if len(execution_list) > 0:
            print("### execution")
            for index, execution in enumerate(execution_list):
                print_execution(execution, "runtime_error", "txt")
                print_execution(execution, "diff", "txt")
                print_execution(execution, "in", "txt")
                print_execution(execution, "out", "txt")
                print_execution(execution, "expected", "txt")


def main():
    """
    コマンドライン引数を解析し、JSONデータを読み取ってMarkdown形式に変換します。

    Note:
    - コマンドライン引数としてJSONファイルのパスを指定することで、そのファイルを読み込みます。
    - ファイルパスが指定されない場合、標準入力からJSONデータを読み込みます。
    - 読み込んだデータは `convert_md` 関数を使用してMarkdown形式に変換されます。
    """
    parser = argparse.ArgumentParser(
        description="このスクリプトは学生データを含むJSONファイルを読み込み、それをMarkdown形式で出力します。"
    )
    parser.add_argument(
        "json_path",
        help="学生情報が含まれているJSONファイルのパス。指定しない場合、標準入力からJSONデータを読み込みます。",
        default=None,
        nargs="?",
    )
    args = parser.parse_args()

    if args.json_path:
        json_path = Path(args.json_path)
        convert_md(json_path.read_text(), json_path.name)
    else:
        json_str = sys.stdin.read()
        convert_md(json_str, "out.md")


if __name__ == "__main__":
    main()
