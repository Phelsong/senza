import os
import shutil
from pydantic import BaseModel

matrix: dict = {}
protected: set = {
    "def",
    "in",
    "for",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    ":",
    "str",
    "set",
    "dict",
    "list",
}

root = os.getcwd()


def main():
    print(root)
    with open(f"{root}/comp_test.py", "r") as fi:
        data = fi.readlines()
        parse_data(data)


def check_indent(arr: list, start_idx: int) -> bool:
    print(arr)
    try:
        assert arr[start_idx + 1] == ""
        assert arr[start_idx + 2] == ""
        assert arr[start_idx + 3] == ""
        return True
    except AssertionError:
        return False
    except IndexError:
        return False


def parse_data(data: list):
    for i, line in enumerate(data):
        divd: list[str] = line.split(" ")
        #
        counter: int = 0

        for idx, x in enumerate(divd):
            #
            if idx == 0 and x == "":
                ind = check_indent(divd, idx)
                while ind:
                    counter += 4
                    ind = check_indent(divd, idx + counter)
                if counter > 0:
                    counter -= 1
                    print(i, counter)
            #
            if x in protected:
                continue


def write_out(data):
    with open(f"{root}/out/comp_test.py", "w") as fo:
        for line in data:
            fo.write(line)


if __name__ == "__main__":
    main()
