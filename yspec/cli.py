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
import sys
import pathlib
import ruyaml

from .checker import check, FormatError


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


def load_file(filename: str, version="1.2"):
    if pathlib.Path(filename).suffix not in ('.yml', '.yaml', '.json'):
        print(f'Unknown extension of file "{filename}"')
        sys.exit(1)
    with open(filename, 'r') as stream:
        try:
            return ruyaml.round_trip_load(stream, version=version)
        except ruyaml.parser.ParserError as e:
            print(e)
            sys.exit(1)


def run():
    args = parse_argv()
    schemafile = args.schemafile[0]
    rules = load_file(schemafile)

    for df in args.datafile:
        data = load_file(df, "1.1")
        try:
            check(data, rules)
        except FormatError as e:
            print(f'Data File "{df}" Errors:')
            print(f'\tline {e.line}: {e.message}')
            if e.errors:
                for ee in e.errors:
                    if 'Input data for' in ee.message:
                        continue
                    print(f'\tline {ee.line}: {ee.message}')
            print(f'Schema File "{schemafile}" line {rules[e.rule].lc.line}, Rule: "{e.rule}"')
            print("")
            sys.exit(1)
