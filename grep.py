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


def output(line):
    """Unittest output function"""

    print(line)

def clean_line(line, params):
    """The function removes minor spaces and \n
    from the string, and lowercase if required
    """

    cleaned_line = line
    if params.ignore_case:
        cleaned_line = cleaned_line.lower()
    return cleaned_line

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

def output_line(index, params, lines, delimiter):
    """The correct output information, in accordance with the parameters"""

    if params.line_number:
        output(str(index + 1) + delimiter + lines[index])
    else:
        output(lines[index])

def count_lines(lines, params):
    """The function which print count of strings that match the pattern"""

    counter = 0

    if params.ignore_case:
        params.pattern = params.pattern.lower()

    for index, _ in enumerate(lines):
        lines[index] = lines[index].rstrip('\n').rstrip()
        cleaned_line = clean_line(lines[index], params)

        if params.invert ^ find_pattern(params.pattern, cleaned_line):
            counter += 1
    output(str(counter))

def parse_lines(lines, params):
    """Creates a list of required strings that match the pattern and parameters
    max_after and max_before - variables that keeping count the number of lines
    to print before and after the found one
    before_matches - the container for the rows that will need to withdraw in
    the presence of parameter before_context or context"""

    max_after = params.after_context
    max_before = params.before_context
    if params.context:
        max_after = max_before = params.context

    before_matches = []
    after_counter = 0

    if params.ignore_case:
        params.pattern = params.pattern.lower()

    for index, _ in enumerate(lines):
        lines[index] = lines[index].rstrip('\n').rstrip()
        cleaned_line = clean_line(lines[index], params)

        if params.invert ^ find_pattern(params.pattern, cleaned_line):
            if before_matches:
                for i in before_matches:
                    output_line(i, params, lines, "-")
                before_matches = []
            if max_after:
                after_counter = max_after
            output_line(index, params, lines, ":")
        elif after_counter:
            after_counter -= 1
            output_line(index, params, lines, "-")
        elif max_before:
            if len(before_matches) >= max_before:
                before_matches.pop(0)
            before_matches.append(index)

def grep(lines, params):
    """UNIX grep realization"""

    if not params.count:
        parse_lines(lines, params)
    else:
        count_lines(lines, params)

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
