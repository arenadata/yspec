# yspec

yspec is a deadly simple checker for structures. It is especially usefull for validation of different yaml/json/toml files

## Usage from cli

yspec ./schema.yaml /tmp/data.json

## Schema Format

Schema is a dict of rules. Every rule do some check according to 'match' field. Schema must include 'root' rule which is applied on top object in structure.

For example structure (in YAML):

```yaml
---
- 'string1'
- 'string2'

```

will be valid for schema (in YAML):

```yaml
---
root:
  match: dict
  item: string
  
string:
  match: string
```
