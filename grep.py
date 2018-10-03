"""
The module implements the grep function as well as some of its keys:
  -h, --help         show this help message and exit
  -v                 Selected lines are those not matching pattern.
  -i                 Perform case insensitive matching.
  -c                 Only a count of selected lines is written to standard
                     output.
  -n                 Each output line is preceded by its relative line number
                     in the file, starting at line 1.
  -C CONTEXT         Print num lines of leading and trailing context
                     surrounding each match.
  -B BEFORE_CONTEXT  Print num lines of trailing context after each match
  -A AFTER_CONTEXT   Print num lines of leading context before each match.
"""


import argparse
import sys


def clean_line(line, params):
    """The function removes minor spaces and \n
    from the string, and lowercase if required
    """

    line = line.rstrip('\n')
    cleaned_line = line
    if params.ignore_case:
        cleaned_line = cleaned_line.lower()
    return cleaned_line

def append_match(index, delimiter, match, matches):
    """Adds a string if it is not in the list"""

    if match not in matches:
        matches[match] = [index, delimiter]
    elif matches[match][1] is '-' and delimiter is ':':
        matches[match][1] = delimiter

def add_lines(matches, index, lines, params):
    """Adds the appropriate strings to the array,
    as well as the strings around them, if necessary
    """

    start_idx = index
    last_idx = index
    if params.context > 0:
        start_idx = index - params.context
        if start_idx < 0:
            start_idx = 0
        last_idx = index + params.context
        if last_idx >= len(lines):
            last_idx = len(lines) - 1
    elif params.after_context > 0:
        last_idx = index + params.after_context
        if last_idx >= len(lines):
            last_idx = len(lines) - 1
    elif params.before_context > 0:
        start_idx = index - params.before_context
        if start_idx < 0:
            start_idx = 0

    for i in range(start_idx, last_idx + 1):
        if i is not index:
            append_match(i + 1, '-', lines[i], matches)
        else:
            append_match(i + 1, ':', lines[i], matches)

def find_pattern(pattern, line):
    """Recursively (just for *) looks for a pattern in the input string"""

    for l_idx in range(0, len(line)):
        temp_idx = l_idx
        for p_idx, _ in enumerate(pattern):
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
    """Creates a list of required strings that match the pattern and parameters"""

    matches = {}
    if params.ignore_case:
        params.pattern = params.pattern.lower()

    for index, line in enumerate(lines):
        cleaned_line = clean_line(line, params)

        if params.invert ^ find_pattern(params.pattern, cleaned_line):
            add_lines(matches, index, lines, params)

    return matches

def output(line):
    """Unittest output function"""

    print(line)

def output_matches(matches, params):
    """The correct output information, in accordance with the parameters"""

    if not params.count:
        for key in matches:
            if params.context or params.after_context or params.before_context:
                if params.line_number:
                    output(str(matches[key][0]) + matches[key][1] + key)
                else:
                    output(key)
            else:
                if params.line_number:
                    output(str(matches[key][0]) + matches[key][1] + key)
                else:
                    output(key)
    else:
        output(str(len(matches)))

def grep(lines, params):
    """UNIX grep realization"""

    matches = parse_lines(lines, params)
    output_matches(matches, params)

def parse_args(args):
    """Сommand line argument parser"""

    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False,
        help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False,
        help='Perform case insensitive matching.')
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
        help='Each output line is preceded by its relative line number \
             in the file, starting at line 1.')
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
    parser.add_argument('pattern', action="store",
                        help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    """Main function, calls the argument parsing and processing"""
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
