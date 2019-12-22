import sys
import argparse

from schemadiff.compare import SchemaComparator, Schema


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


def main():
    args = parse_args()
    old_schema = Schema.from_sdl(args.old_schema.read())
    new_schema = Schema.from_sdl(args.new_schema.read())
    args.old_schema.close()
    args.new_schema.close()

    diff = SchemaComparator(old_schema, new_schema).compare()


if __name__ == '__main__':
    sys.exit(main())
