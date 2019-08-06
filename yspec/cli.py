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

import sys
import yaml

from pprint import pprint
from .checker import process_rule, FormatError



def run(argv):
    with open("./schema.yaml", 'r') as stream:
        rules = yaml.safe_load(stream)

    with open(argv[1], 'r') as stream:
        data = yaml.safe_load(stream)

    try:
        process_rule(data, rules, 'root', ['.'])
    except FormatError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Got an error {}".format(str(e)))
        if e.data is not None:
            print("At block")
            print("--------")
            pprint(e.data, depth=1)
        print("--------------------------------------------------")
        print("")
        sys.exit(1)
