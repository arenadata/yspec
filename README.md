# yspec

yspec is a deadly simple checker for structures. It is especially usefull for validation of different yaml/json files

## Usage from cli

```sh
yspec ./schema.yaml /tmp/data.json
```

NOTE: yspec able to take json/yaml/toml for schema and for data

## Usage from code

```python
from yspec.checker import process_rule

# Some code that prepares data and rules

process_rule(data, rules, 'root')
```

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

## Match Rules

### Simple type matches

#### String

```yaml
my_awesome_string:
  match: string
```

#### Boolean

```yaml
my_awesome_bool:
  match: bool
```

#### Integer

```yaml
my_awesome_int:
  match: int
```

#### Float

```yaml
my_awesome_float:
  match: float
```

### Recursion type matches

There are two of them: dict and list. Both has the same recursion logic. At first we apply some checks on object itself, and then apply another (or the same) rule to childrens (list elements, or values of dict).

#### List

```yaml
my_list:
  match: list
  item: some_other_rule
```

List is a recurent type. Fist it checks is the object a list, then it check every element according to rule in 'item' attr.


#### Dict

```yaml
my_list:
  match: dict
  items:
    key1: string_rule
    key2: integer_rule
  default_item: some_other_rule
  required_items:
    - key2
```

That is a rule that describe a dict that has two keys (key1 and key2). One of keys (key2) is mandatory. Key1 should be checked according to 'string_rule' rule, while any other keys with any other (non key1 or key2) name will be checked according to some_other_rule.


If we has remove default_item
```yaml
my_list:
  match: dict
  items:
    key1: string_rule
    key2: integer_rule
  required_items:
    - key2
```

A dict could be with two keys (key1, key2) maximum


### Sample of simple and recursion matches

Schema:

```yaml
---
boolean:
  match: bool

string:
  match: string

integer:
  match: int

float:
  match: float

list:
  match: list
  item: string

root:
  match: dict
  items:
    key1: boolean
    key2: string
    key3: integer
    key4: float
    key5: list
```

Data:
```yaml
---
key1: true
key2: "That is a string"
key3: 1
key4: 1.0
key5:
  - "One more string"
  - "Another string"
```

### Special matches

#### OneOf match

```yaml
constraint_list_item:
  match: one_of
  variants:
    - integer_rule
    - some_other_rule
```

OneOf match success if any of rules from "variants" success.

#### Dict key selection

Some times you need to do a separate checks for dict that have some key/value pair.

For example you have the following data:
```yaml
---
- type: type1
  payload:
    - 1
    - 1
- type: type2
  payload:
    - "that is a string"
    - "that is a string2"
```

In that example you have a dict wich has diffent payload depends of type key. That is possible to describe with following schema:

```yaml
---
root:
  match: list
  item: list_item

list_item:
  match: dict_key_selection
  selector: type
  variants:
    type1: dict_with_int
    type2: dict_with_string

dict_with_int:
  match: dict
  items:
    type: string
    payload: list_of_int
  required_items:
    - type
    - payload

dict_with_string:
  match: dict
  items:
    type: string
    payload: list_of_string
  required_items:
    - type
    - payload
  

list_of_int:
  match: list
  item: int
  
int:
  match: int
  
list_of_string:
  match: list
  item: string
  
string:
  match: string
```
