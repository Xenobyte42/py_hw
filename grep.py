
import argparse
import sys
import re


def clean_line(line, params):
    cleaned_line = line.rstrip().rstrip('\n')
    if params.ignore_case:
        cleaned_line = cleaned_line.lower()
    return cleaned_line

def append_match(match, matches):
    if match not in matches:
        matches.append(match)

def add_lines(matches, index, lines, params):
    start_idx = 0
    last_idx = 0
    if params.context > 0:
        start_idx = index - params.context
        if start_idx < 0:
            start_idx = 0
        last_idx = index + params.context
        if last_idx >= len(lines):
            last_idx = len(lines) - 1
    elif params.after_context > 0:
        start_idx = index
        last_idx = index + params.after_context
        if last_idx >= len(lines):
            last_idx = len(lines) - 1
    elif params.before_context > 0:
        start_idx = index - params.before_context
        if start_idx < 0:
            start_idx = 0
        last_idx = index
    else:
        start_idx = index
        last_idx = index
    for i in range(start_idx, last_idx + 1):
            lines[i] = lines[i].rstrip('\n')
            append_match([i + 1, lines[i]], matches)

def find_pattern(pattern, line):
    for l_idx in range(0, len(line)):
        temp_idx = l_idx
        for p_idx in range(0, len(pattern)):
            if temp_idx == len(line):
                break

            if pattern[p_idx] == '?':
                temp_idx += 1
            elif pattern[p_idx] == '*':
                if len(pattern) == 1:
                    return True
                return find_pattern(pattern[p_idx + 1:], line[temp_idx:])
            else:
                if pattern[p_idx] == line[temp_idx]:
                    temp_idx += 1
                else:
                    break
    
            if p_idx == len(pattern) - 1:
                return True
    return False

def parse_lines(lines, params):
    matches = []
    if params.ignore_case:
        params.pattern = params.pattern.lower()

    for index, line in enumerate(lines):
        line = line.rstrip('\n')
        cleaned_line = clean_line(line, params)

        if params.invert:
            if find_pattern(params.pattern, cleaned_line) is False:
                add_lines(matches, index, lines, params)
        else:
            if find_pattern(params.pattern, cleaned_line) is True:
                add_lines(matches, index, lines, params)
    return matches

def output(line):
    print(line)

def output_matches(matches, params):
    if params.count:
        output(str(len(matches)))
    else:
        if params.context or params.after_context or params.before_context:
            last_idx = -2
            for match in matches:
                if match[0] - last_idx > 1:
                    print("--")
                last_idx = match[0]
                if params.line_number:
                    print(match[0], '-', sep="", end="")
                    output(match[1])
                else:
                    output(match[1])
            print("--")
        else:
            for match in matches:
                if params.line_number:
                    print(match[0], ':', sep="", end="")
                    output(match[1])
                else:
                    output(match[1])

def grep(lines, params):
    matches = parse_lines(lines, params)
    output_matches(matches, params)

def parse_args(args):
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
