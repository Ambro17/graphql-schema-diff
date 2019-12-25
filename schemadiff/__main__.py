import sys
import argparse

from schemadiff.changes import Change, Criticality
from schemadiff.diff.schema import Schema
from schemadiff.graphql_schema import GraphQLSchema


def parse_args(arguments):
    parser = argparse.ArgumentParser(description='Mi cli')
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
    parser.add_argument('-t', '--tolerant',
                        action='store_true',
                        help="Tolerant mode. Error out only if there's a breaking change but allow dangerous changes")
    parser.add_argument('-s', '--strict',
                        action='store_true',
                        help="Strict mode. Error out on dangerous and breaking changes.")
    return parser.parse_args(arguments)


def main(args):
    # Load schemas from file path args
    old_schema = GraphQLSchema.from_sdl(args.old_schema.read())
    new_schema = GraphQLSchema.from_sdl(args.new_schema.read())
    args.old_schema.close()
    args.new_schema.close()

    diff = Schema(old_schema, new_schema).diff()
    print(format_diff(diff))

    return exit_code(diff, args.strict, args.tolerant)


def format_diff(changes: [Change]) -> str:
    changes = '\n'.join(
        format_change_by_criticality(change)
        for change in changes
    )
    return changes or '🎉 Both schemas are equal!'


def format_change_by_criticality(change: Change) -> str:
    icon_by_criticality = {
        Criticality.Breaking: '❌',
        Criticality.Dangerous: '🚸',
        Criticality.NonBreaking: '✅',
    }
    icon = icon_by_criticality[change.criticality.level]
    return f"{icon} {change.message}"


def exit_code(changes, strict, tolerant):
    exit_code = 0
    if strict and any(change.breaking or change.dangerous for change in changes):
        exit_code = 1
    elif tolerant and any(change.breaking for change in changes):
        exit_code = 1

    return exit_code


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    sys.exit(main(args))
