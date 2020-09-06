import sys
import argparse

from schemadiff.allow_list import read_allowed_changes
from schemadiff.diff.schema import Schema
from schemadiff.schema_loader import SchemaLoader
from schemadiff.formatting import print_diff, print_json
from schemadiff.validation import rules_list, evaluate_rules


def cli():
    args = parse_args(sys.argv[1:])
    return main(args)


def parse_args(arguments):
    parser = argparse.ArgumentParser(description='Schema comparator')
    parser.add_argument('-o', '--old-schema',
                        dest='old_schema',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        help='Path to old graphql schema file',
                        required=True)
    parser.add_argument('-n', '--new-schema',
                        dest='new_schema',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        help='Path to new graphql schema file',
                        required=True)
    parser.add_argument('-j', '--as-json',
                        action='store_true',
                        help='Output a detailed summary of changes in json format',
                        required=False)
    parser.add_argument('-a', '--allow-list',
                        type=argparse.FileType('r', encoding='UTF-8'),
                        help='Path to the allowed list of changes')
    parser.add_argument('-t', '--tolerant',
                        action='store_true',
                        help="Tolerant mode. Error out only if there's a breaking change but allow dangerous changes")
    parser.add_argument('-s', '--strict',
                        action='store_true',
                        help="Strict mode. Error out on dangerous and breaking changes.")
    parser.add_argument('-r', '--validation-rules', choices=rules_list(), nargs='*',
                        help="Evaluate rules mode. Error out on changes that fail some validation rule.")

    return parser.parse_args(arguments)


def main(args) -> int:
    # Load schemas from file path args
    old_schema = SchemaLoader.from_sdl(args.old_schema.read())
    new_schema = SchemaLoader.from_sdl(args.new_schema.read())
    args.old_schema.close()
    args.new_schema.close()

    diff = Schema(old_schema, new_schema).diff()
    restricted = evaluate_rules(diff, args.validation_rules)
    if args.allow_list:
        allow_list = args.allow_list.read()
        args.allow_list.close()
        allowed_changes = read_allowed_changes(allow_list)
        diff = [change for change in diff if change.checksum() not in allowed_changes]
    if args.as_json:
        print_json(diff)
    else:
        print_diff(diff)

    return exit_code(diff, args.strict, restricted, args.tolerant)


def exit_code(changes, strict, restricted, tolerant) -> int:
    exit_code = 0
    if strict and any(change.breaking or change.dangerous for change in changes):
        exit_code = 1
    if restricted:
        exit_code = 1
    elif tolerant and any(change.breaking for change in changes):
        exit_code = 1

    return exit_code


if __name__ == '__main__':
    sys.exit(cli())
