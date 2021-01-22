# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


import ruyaml


class FormatError(Exception):
    def __init__(self, path, message, data=None, caused_by=None, rule=None, parent=None):
        self.path = path
        self.message = message
        self.data = data
        self.rule = rule
        self.errors = caused_by
        self.parent = parent
        self.line = None
        if isinstance(data, ruyaml.comments.CommentedBase):
            self.line = data.lc.line
        elif parent:
            self.line = parent.lc.line
        super().__init__(message)

    def __str__(self):
        message = f"at {self.path}: {self.message}"
        if self.errors is not None:
            for e in self.errors:
                message = message + "\n" + str(e)
        return message


class SchemaError(Exception):
    pass


class DataError(Exception):
    pass


def fp(path):
    return '/'.join(path)


def check_type(data, data_type, path, rule=None, parent=None):
    if not isinstance(data, data_type):
        last = path[-1]
        msg = '{} "{}" should be a {}'.format(last[0], last[1], str(data_type))
        raise FormatError(path, msg, data, rule=rule, parent=parent)


def match_list(data, rules, rule, path, parent=None):
    check_type(data, list, path, rule, parent=parent)
    for i, v in enumerate(data):
        process_rule(
            v, rules, rule['item'], path=path + [('Value of list index', i)], parent=parent
        )
    return True


def match_dict(data, rules, rule, path, parent=None):
    check_type(data, dict, path, rule)
    if 'required_items' in rule:
        for i in rule['required_items']:
            if i not in data:
                raise FormatError(path, f'There is no required key "{i}" in map', data, rule=rule)
    for k in data:
        new_path = path + [('Value of map key', k)]
        if 'items' in rule and k in rule['items']:
            process_rule(data[k], rules, rule['items'][k], new_path, parent=data)
        elif 'default_item' in rule:
            process_rule(data[k], rules, rule['default_item'], new_path, parent=data)
        else:
            raise FormatError(path, f'Map key "{k}" is not allowed here', data, rule=rule)


def match_dict_key_selection(data, rules, rule, path, parent=None):
    check_type(data, dict, path, rule, parent=parent)
    key = rule['selector']
    if key not in data:
        raise FormatError(
            path, f'There is no key "{key}" in that map.', data, rule=rule, parent=parent
        )
    value = data[key]
    if value in rule['variants']:
        process_rule(data, rules, rule['variants'][value], path, parent=parent)
    elif 'default_variant' in rule:
        process_rule(data, rules, rule['default_variant'], path, parent=parent)
    else:
        msg = f'Value "{value}" is not allowed for map key "{key}".'
        raise FormatError(path, msg, data, rule=rule, parent=parent)


def match_one_of(data, rules, rule, path, parent=None):
    errors = []
    for obj in rule['variants']:
        try:
            process_rule(data, rules, obj, path)
        except FormatError as e:
            errors.append(e)
    if len(errors) == len(rule['variants']):
        raise errors[-1]
        #raise FormatError(path, "None of the variants match", data, errors, rule)


def match_set(data, rules, rule, path, parent=None):
    if data not in rule['variants']:
        msg = f'Value "{data}" not in set {rule["variants"]}'
        raise FormatError(path, msg, data, rule=rule, parent=parent)


def match_simple_type(obj_type):
    def match(data, rules, rule, path, parent=None):
        check_type(data, obj_type, path, rule, parent=parent)
    return match


MATCH = {
    'list': match_list,
    'dict': match_dict,
    'one_of': match_one_of,
    'dict_key_selection': match_dict_key_selection,
    'set': match_set,
    'string': match_simple_type(str),
    'bool': match_simple_type(bool),
    'int': match_simple_type(int),
    'float': match_simple_type(float),
}


def check_rule(rules):
    if not isinstance(rules, dict):
        return (False, 'YSpec should be a map')
    if 'root' not in rules:
        return (False, 'YSpec should has "root" key')
    if 'match' not in rules['root']:
        return (False, 'YSpec should has "match" subkey of "root" key')
    return (True, '')


def process_rule(data, rules, name, path=None, parent=None):
    if path is None:
        path = []
    if name not in rules:
        raise SchemaError(f"There is no rule {name} in schema.")
    rule = rules[name]
    if 'match' not in rule:
        raise SchemaError(f"There is no mandatory match attr in rule {rule} in schema.")
    match = rule['match']
    if match not in MATCH:
        raise SchemaError(f"Unknown match {match} from schema. Donno how to handle that.")

    # print(f'process_rule: {MATCH[match].__name__} "{name}" path: {path}, data: {data}')
    MATCH[match](data, rules, rule, path=path, parent=parent)


def check(data, rules):
    if not isinstance(data, ruyaml.comments.CommentedBase):
        raise DataError("You should use ruyaml.round_trip_load() to parse date yaml")
    if not isinstance(rules, ruyaml.comments.CommentedBase):
        raise SchemaError("You should use ruyaml.round_trip_load() to parse schema yaml")
    process_rule(data, rules, 'root')
