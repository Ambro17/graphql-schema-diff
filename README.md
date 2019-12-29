<p align="center">
  <img src="https://raw.githubusercontent.com/Ambro17/graphql-schema-diff/integrations/images/logo.svg?sanitize=true" title="Logo">
</p>

[![Build Status](https://travis-ci.com/Ambro17/graphql-schema-diff.svg?branch=master)](https://travis-ci.com/Ambro17/graphql-schema-diff)
[![codecov](https://codecov.io/gh/Ambro17/graphql-schema-diff/branch/master/graph/badge.svg)](https://codecov.io/gh/Ambro17/graphql-schema-diff)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4e998e6c1f71468a93d0a34a41b554bb)](https://www.codacy.com/manual/Ambro17/graphql-schema-diff?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Ambro17/graphql-schema-diff&amp;utm_campaign=Badge_Grade)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-orange.svg)](https://www.python.org/downloads/release/python-360/)

# schemadiff
`schemadiff` is a lib that shows you the difference between two GraphQL Schemas.
It takes two schemas from a string or a file and gives you a list of changes between both versions.
This might be useful for
*  Detecting breaking changes before they reach the api clients
*  Integrating into CI pipelines to control your api evolution
*  Document your api changes and submit them for approval along with your pull requests.

## Installation
The lib requires python3.6 or greater to work. In order to install it run
```bash
$ python3 -m pip install graphql-schema-diff
```

## Usage
You can use this package as a lib or as a cli. You can choose what better suits your needs
### Lib
```python
>>> from schemadiff import diff, diff_from_file, format_diff
>>> old_schema = """
schema {
    query: Query
} 

type Query {
    a: Int!,
    sum(start: Float=0): Int
}
"""
>>> new_schema = """
schema {
    query: Query
} 

type Query {
    b: String,
    sum(start: Float=1): Int
}
"""
>>> changes = diff(old_schema, new_schema)
>>> print(format_diff(changes))                   # Pretty print difference
>>> any(change.breaking or change.dangerous for change in changes)    # Check if there was any breaking or dangerous change

# You can also compare from schema files
>>> with open('old_schema.gql', 'w') as f:
...     f.write(old_schema)
>>> with open('new_schema.gql', 'w') as f:
...     f.write(new_schema)
>>> changes = diff_from_file('old_schema.gql', 'new_schema.gql')
>>> print(format_diff(changes))
```
### CLI
Inside your virtualenv you can invoke the entrypoint to see its usage options
```bash
$ schemadiff -h
Usage: schemadiff [-h] -o OLD_SCHEMA -n NEW_SCHEMA [-t] [-s]

Schema comparator

optional arguments:
  -h, --help            show this help message and exit
  -o OLD_SCHEMA, --old-schema OLD_SCHEMA
                        Path to old graphql schema file
  -n NEW_SCHEMA, --new-schema NEW_SCHEMA
                        Path to new graphql schema file
  -t, --tolerant        Tolerant mode. Error out only if there's a breaking
                        change but allow dangerous changes
  -s, --strict          Strict mode. Error out on dangerous and breaking
                        changes.
```
#### Examples
`$ schemadiff -o tests/data/simple_schema.gql -n tests/data/new_schema.gql`

`$ schemadiff --old-schema tests/data/simple_schema.gql -n tests/data/new_schema.gql --tolerant`

`$ schemadiff -o tests/data/simple_schema.gql --new-schema tests/data/new_schema.gql --strict`

#### Sample output
```bash
✔️ Field `c` was added to object type `Query`
❌ Field `a` was removed from object type `Query`
⚠️ Default value for argument `x` on field `Field.calculus` changed from `0` to `1`
```

>If you run the cli and see a replacement character (�) or a square box (□) instead of the emojis run
>```bash
>$ sudo apt install fonts-noto-color-emoji
>$ fc-cache -f -v
>```
>That should install noto emoji fonts and refresh the font cache so you can see the proper emojis 😎

## Credits
Implementation was heavily inspired by Marc Giroux [ruby version](https://github.com/xuorig/graphql-schema_comparator) 
and Kamil Kisiela [js implementation](https://github.com/kamilkisiela/graphql-inspector).

## Contributions
Bug reports, Feature requests or pull request are welcome!
