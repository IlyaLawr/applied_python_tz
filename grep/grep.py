
import argparse
import sys
import re

def output(line: str) -> None:
    print(line)


def grep(lines: list, params: argparse.ArgumentParser) -> None:

    def check_lines(lines: tuple, pattern: str, ignore_case: bool, invert: bool) -> str:
        if ignore_case:
            if invert:
                yield from [line for line in lines if not re.search(pattern, line, flags=re.IGNORECASE)]
            else:
                yield from [line for line in lines if re.search(pattern, line, flags=re.IGNORECASE)]
        else:
            if invert:
                yield from [line for line in lines if not re.search(pattern, line)]
            else:
                yield from [line for line in lines if re.search(pattern, line)]

    lines = tuple(map(str.strip, lines))
    length = len(lines)

    pattern = params.pattern.replace('?', '.').replace('*', '.*')
    pattern_lines = check_lines(lines, pattern, params.ignore_case, params.invert)

    result = {}

    if not any((params.context, params.before_context, params.after_context)):
        if not params.count:
            if not params.line_number:
                for line in pattern_lines:
                    output(line)
            else:
                pattern_line = next(pattern_lines, None)
                while pattern_line:
                    index = lines.index(pattern_line)
                    result[lines[index]] = f'{index + 1}:'
                    pattern_line = next(pattern_lines, None)
        else:
            output(f'{len([*pattern_lines])}')
    else:
        params_context = params.context or params.before_context or params.after_context
        pattern_line = next(pattern_lines, None)

        while pattern_line:
            index = lines.index(pattern_line)
            start = 0 if index - params_context < 0 else index - params_context
            stop = length if (index + params_context) >= length else (index + params_context) + 1

            if not params.after_context:
                for i in range(start, index):
                    result[lines[i]] = result.get(lines[i], f'{i + 1}-')

            result[lines[index]] = f'{index + 1}:'

            if not params.before_context:
                for i in range(index + 1, stop):
                    result[lines[i]] = result.get(lines[i], f'{i + 1}-')

            pattern_line = next(pattern_lines, None)

    if not params.line_number:
        for line in result:
            output(line)
    else:
        for line, number in result.items():
            output(f'{number}{line}')


def parse_args(args: list[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
