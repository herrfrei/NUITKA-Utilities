#     Copyright 2019, Jorj McKie, mailto:<jorj.x.mckie@outlook.de>
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
""" This script invokes the Nuitka compiler.
Any option for the Nuitka command line can be entered as an item in list
'my_opts'. This can be used to create "canned" standard compilation profiles
and to limit the command line length.

This special version performs standalone compilations and serves as an invoker
for the user plugin "hinted-mods.py". This plugin controls the inclusion of
modules in the distribution folder.
"""
import sys
import os
import json
from nuitka.__main__ import main

my_opts = [
    "--standalone",  # the purpose of this script
    "--python-flag=nosite",  # change this if needed
    "--remove-output",  # delete this if you want
    "--experimental=use_pefile",  # will become standard soon
]

if sys.platform == "win32":
    my_opts.append("--mingw64")  # change this as required
    my_opts.append("--disable-dll-dependency-cache")  # at your discretion ...

script = sys.argv[-1]  # name of script to be compiled
if not os.path.exists(script):
    raise ValueError("No such file: " + script)

filename, extname = os.path.splitext(script)
json_fname = filename + ".json"

if extname.lower() == ".pyw":
    my_opts.append("--windows-disable-console")

if not os.path.exists(json_fname):
    raise ValueError("No such file: " + json_fname)

# invoke user plugin to work with the JSON file
my_opts.append("--user-plugin=hinted-mods.py=" + json_fname)

# now build a new sys.argv array
new_sysargs = [sys.argv[0]]
for o in my_opts:
    new_sysargs.append(o)

new_sysargs.extend(sys.argv[1:])

sys.argv = new_sysargs

# keep user happy with some type of protocol
print("NUITKA is compiling '%s' with these options:" % sys.argv[-1])
for o in sys.argv[1:-1]:
    print(" " + o)
print(" ")

main()
