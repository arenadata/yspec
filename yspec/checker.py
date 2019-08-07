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


class FormatError(Exception):
    def __init__(self, path, message, data=None, caused_by=None):
        self.path = fp(path)
        self.message = message
        self.data = data
        self.errors = caused_by

    def __str__(self):
        message = f"at {self.path}: {self.message}" 
        if self.errors is not None:
            for e in self.errors:
                message = message + "\n" + str(e)
        return message


class SchemaError(Exception):
    pass


def fp(path):
    return '/'.join(path)


def check_type(data, data_type, path):
    if not isinstance(data, data_type):
        raise FormatError(path, 'Object should be a {}'.format(str(data_type)), data)


def match_list(data, rules, rule, path):
    check_type(data, list, path)
    for i, v in enumerate(data):
        process_rule(v, rules, rule['item'], path + [str(i)])
    return True


def match_dict(data, rules, rule, path):
    check_type(data, dict, path)
    if 'required_items' in rule:
        for i in rule['required_items']:
            if i not in data:
                raise FormatError(path, f"There is no required item {i} in dict", data)
    for k, v in data.items():
        if 'items' in rule and k in rule['items']:
            process_rule(data[k], rules, rule['items'][k], path + [k])
        elif 'default_item' in rule:
            process_rule(data[k], rules, rule['default_item'], path + [k])
        else:
            raise FormatError(path, f"No item rule for {k}", data)


def match_dict_key_selection(data, rules, rule, path):
    check_type(data, dict, path)
    key = rule['selector']
    if key not in data:
        raise FormatError(path, f"There is no type in that dict", data)
    value = data[key]
    if value in rule['variants']:
        process_rule(data, rules, rule['variants'][value], path)
    elif 'default_variant' in rule:
        process_rule(data, rules, rule['default_variant'], path)
    else:
        raise FormatError(path, f"There is no '{key}: {value}' allowed here.", data)


def match_one_of(data, rules, rule, path):
    errors = []
    for obj in rule['variants']:
        try:
            process_rule(data, rules, obj, path)
        except FormatError as e:
            errors.append(e)
    if len(errors) == len(rule['variants']):
        raise FormatError(path, "None of the variants match", data, errors)


def match_simple_type(obj_type):
    def match(data, rules, rule, path):
        check_type(data, obj_type, path)
    return match


MATCH = {
    'list': match_list,
    'dict': match_dict,
    'one_of': match_one_of,
    'dict_key_selection': match_dict_key_selection,
    'string': match_simple_type(str),
    'bool': match_simple_type(bool),
    'int': match_simple_type(int),
    'float': match_simple_type(float),
}


def process_rule(data, rules, name, path=['.']):
    if name not in rules:
        raise SchemaError(f"There is no rule {name} in schema.")
    rule = rules[name]
    if 'match' not in rule:
        raise SchemaError(f"There is no mandatory match attr in rule in schema.")
    match = rule['match']
    if match not in MATCH:
        raise SchemaError(f"Unknown match {match} from schema. Donno how to handle that.")

    MATCH[match](data, rules, rule, path)
