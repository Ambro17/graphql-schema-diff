<p align="center">
  <img src="https://raw.githubusercontent.com/Ambro17/graphql-schema-diff/master/images/logo.svg?sanitize=true" title="Logo">
</p>
<p align="center">
    <a href="https://travis-ci.com/Ambro17/graphql-schema-diff">
        <img alt="Build status" src="https://travis-ci.com/Ambro17/graphql-schema-diff.svg?branch=master">
    </a>
    <a href="https://codecov.io/gh/Ambro17/graphql-schema-diff">
        <img alt="codecov" src="https://codecov.io/gh/Ambro17/graphql-schema-diff/branch/master/graph/badge.svg">
    </a>
    <a href="https://www.codacy.com/manual/Ambro17/graphql-schema-diff?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Ambro17/graphql-schema-diff&amp;utm_campaign=Badge_Grade">
        <img alt="Codacy" src="https://api.codacy.com/project/badge/Grade/4e998e6c1f71468a93d0a34a41b554bb">
    </a>
    <a href="https://www.gnu.org/licenses/gpl-3.0">
        <img alt="License: GPL v3" src="https://img.shields.io/badge/License-GPLv3-blue.svg">
    </a>
    <a href="https://www.python.org/downloads/release/python-360/">
        <img alt="Python 3.6+" src="https://img.shields.io/badge/Python-3.6+-blue.svg">
    </a>
</p>
<p align="center">
  <img src="https://raw.githubusercontent.com/Ambro17/graphql-schema-diff/master/images/usage.gif" title="Usage">
</p>

# schemadiff
`schemadiff` is a lib that shows you the difference between two GraphQL Schemas.
It takes two schemas from a string or a file and gives you a list of changes between both versions.
This might be useful for:
*  Detecting breaking changes before they reach the api clients
*  Integrating into CI pipelines to control your api evolution
*  Document your api changes and submit them for an approval along with your pull requests.
*  Restricting unwanted changes

## Installation
The lib requires python3.6 or greater to work. In order to install it run
```bash
$ python3 -m pip install graphql-schema-diff
```

## Usage
You can use this package as a lib or as a CLI. You can choose what better suits your needs

### As a Lib
```python
from schemadiff import diff, diff_from_file, print_diff

old_schema = """
schema {
    query: Query
} 

type Query {
    a: Int!,
    sum(start: Float=0): Int
}
"""

new_schema = """
schema {
    query: Query
} 

type Query {
    b: String,
    sum(start: Float=1): Int
}
"""

changes = diff(old_schema, new_schema)
print_diff(changes)                   # Pretty print difference
any(change.breaking or change.dangerous for change in changes)    # Check if there was any breaking or dangerous change

# You can also compare from schema files
with open('old_schema.gql', 'w') as f:
    f.write(old_schema)

with open('new_schema.gql', 'w') as f:
    f.write(new_schema)

changes = diff_from_file('old_schema.gql', 'new_schema.gql')
print_diff(changes)
```
### CLI
Inside your virtualenv you can invoke the entrypoint to see its usage options
```bash
$ schemadiff -h
Usage: schemadiff [-h] -o OLD_SCHEMA -n NEW_SCHEMA [-j] [-a ALLOW_LIST] [-t] [-r] [-s]

Schema comparator

optional arguments:
  -h, --help            show this help message and exit
  -o OLD_SCHEMA, --old-schema OLD_SCHEMA
                        Path to old graphql schema file
  -n NEW_SCHEMA, --new-schema NEW_SCHEMA
                        Path to new graphql schema file
  -j, --as-json         Output a detailed summary of changes in json format
  -a ALLOW_LIST, --allow-list ALLOW_LIST
                        Path to the allowed list of changes
  -t, --tolerant        Tolerant mode. Error out only if there's a breaking
                        change but allow dangerous changes
  -r, --restrictions    Restricted mode. Error out on restricted changes.
  -s, --strict          Strict mode. Error out on dangerous and breaking
                        changes.
```
#### Examples
```bash
# Compare schemas and output diff to stdout
schemadiff -o tests/data/simple_schema.gql -n tests/data/new_schema.gql

# Pass a evaluation flag (mixing long arg name and short arg name)
schemadiff --old-schema tests/data/simple_schema.gql -n tests/data/new_schema.gql --strict

# Print output as json with details of each change
schemadiff -o tests/data/simple_schema.gql -n tests/data/new_schema.gql --as-json

# Save output to a json file
schemadiff -o tests/data/simple_schema.gql -n tests/data/new_schema.gql --as-json > changes.json

# Compare schemas ignoring allowed changes
schemadiff -o tests/data/simple_schema.gql -n tests/data/new_schema.gql -a allowlist.json

# Compare schemas restricting adding new types without description
schemadiff -o tests/data/simple_schema.gql -n simple_schema_new_type_without_description.gql -r add-type-without-description
```

>If you run the cli and see a replacement character (�) or a square box (□) instead of the emojis run
>```bash
>$ sudo apt install fonts-noto-color-emoji
>$ vim ~/.config/fontconfig/fonts.conf # and paste https://gist.github.com/Ambro17/80bce76d07a6eb74323db2ca9b887263
>$ fc-cache -f -v
>```
>That should install noto emoji fonts and set is as the fallback font to render emojis 😎

## Restricting changes
You can use this library to validate whether your schema matches a set of rules.

### Built-in restrictions
The library has its own built-in restrictions ready-to-use. Just append them to the `-r` command in `CLI`. You can
add as many as you want.

- `add-type-without-description`
Restrict adding new GraphQL types without entering a non-empty description.

- `remove-type-description`
Restrict removing the description from an existing GraphQL type.
    
- `add-field-without-description`
Restrict adding fields without description.

- `remove-field-description`
Restrict removing the description from an existing GraphQL field.

- `add-enum-value-without-description`
Restrict adding enum value without description.

- `remove-enum-value-description`
Restrict adding enum value without description.

Running the following command, you could restrict type additions without entering a nice description.
```
# Compare schemas restricting adding new types without description
schemadiff -o tests/data/simple_schema.gql -n simple_schema_new_type_without_description.gql -r add-type-without-description
```


## API Reference
You can also read the [API Reference](https://ambro17.github.io/graphql-schema-diff/) if you want to get a better understanding of the inner workings of the lib

## Credits
Implementation was heavily inspired by Marc Giroux [ruby version](https://github.com/xuorig/graphql-schema_comparator) 
and Kamil Kisiela [js implementation](https://github.com/kamilkisiela/graphql-inspector).

Logo arrows were adapted from the work of [Paul Verhulst @ The Noun Project](https://thenounproject.com/paulverhulst/)

## Contributors
- @Checho3388: Added the whole `evaluate_diff` functionality. Thank you!

You can contribute reporting bugs, writing issues or pull requests for any new features!