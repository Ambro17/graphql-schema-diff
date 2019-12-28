# schemadiff
Compare GraphQL Schemas

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
```
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
```
✅ Field `c` was added to object type `Query`
❌ Field `a` was removed from object type `Query`
🚸 Default value for argument `x` on field `Field.calculus` changed from `0` to `1`
```

>If you run the cli and see a replacement character (�) or a square box (□) instead of the emojis run
>```
>$ sudo apt install fonts-noto-color-emoji
>$ fc-cache -f -v
>```
>That should install noto emoji fonts and refresh the font cache so you can see the proper emojis 😎


## Credits
Implementation was heavily inspired by Marc Giroux [ruby version](https://github.com/xuorig/graphql-schema_comparator) 
and Kamil Kisiela [js implementation](https://github.com/kamilkisiela/graphql-inspector).

## Contributions
Bug reports, Feature requests or pull request are welcome!
