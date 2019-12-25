import sys
import argparse

from schemadiff.changes import Change, Criticality
from schemadiff.diff.schema import Schema
from schemadiff.graphql_schema import GraphQLSchema


def parse_args():
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
    return parser.parse_args()


def format_change_by_criticality(change: Change) -> str:
    icon_by_criticality = {
        Criticality.Breaking: '❌',
        Criticality.Dangerous: '🚸',
        Criticality.NonBreaking: '✅',
    }
    icon = icon_by_criticality[change.criticality.level]
    return f"{icon} {change.message}"


def format_diff(changes: [Change]) -> str:
    changes = '\n'.join(
        format_change_by_criticality(change)
        for change in changes
    )
    return changes or '🎉 Both schemas are equal!'


def main():
    args = parse_args()

    # Load schemas from file path args
    old_schema = GraphQLSchema.from_sdl(args.old_schema.read())
    new_schema = GraphQLSchema.from_sdl(args.new_schema.read())
    args.old_schema.close()
    args.new_schema.close()

    diff = Schema(old_schema, new_schema).diff()
    print(format_diff(diff))


if __name__ == '__main__':
    sys.exit(main())
