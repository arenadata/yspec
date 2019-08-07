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

import argparse
import json
import sys
import yaml

from pprint import pprint
from .checker import process_rule, FormatError


def parse_argv():
    parser = argparse.ArgumentParser(
        description="Validate structured data according to schema"
    )
    parser.add_argument(
        'schemafile',
        help="File with schema description",
        nargs=1
    )
    parser.add_argument(
        'datafile',
        help="File with data to be checked by schema",
        nargs='*'
    )
    return parser.parse_args()


def load_file(filename: str):
    if filename.endswith('.yaml') or filename.endswith('.yml'):
        with open(filename, 'r') as stream:
            return yaml.safe_load(stream)
    elif filename.endswith('.json'):
        with open(filename) as json_file:
            return json.load(json_file)
    raise Exception(f"Unknown extension of file {filename}")


def run():
    args = parse_argv()
    rules = load_file(args.schemafile[0])

    for df in args.datafile:
        data = load_file(df)
        try:
            process_rule(data, rules, 'root')
        except FormatError as e:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(f"File:  {df}")
            print("Error: {}".format(str(e)))
            if e.data is not None:
                print("At block")
                print("--------")
                pprint(e.data, depth=1)
            print("--------------------------------------------------")
            print("")
            sys.exit(1)
