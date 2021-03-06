#     Copyright 2019, Jorj McKie, mailto:jorj.x.mckie@outlook.de
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
"""
This script creates an executable out of the "dist" folder of a Python program,
which has been compiled by Nuitka in standalone mode. This is also known as
"One-File-Distribution".

The executable contains the compressed dist folder and is named like the
script, i.e. "script.exe", and put in the same directory, where the dist
folder lives.

When the installation file is executed, the dist folder is

(1) decompressed in the user's temp directory (envireonment variable $TEMP)
(2) the original 'script.exe' is invoked, passing in any provided arguments
(3) after 'script.exe' has finished, the dist folder is removed again

The following handling option is also available:

Execute the distribution file with parameter '/D=...' by specifying a
directory. This folder will then be used to store 'dist', and the original
script will not be executed as part of the installation process.

Dependencies
------------
* PySimpleGUI
* The program **NSIS** is required to generate the installation file. It can be
  downloaded from here: https://nsis.sourceforge.io/Main_Page.

"""
import sys
import os
import time
import subprocess as sp
import PySimpleGUI as psg

nsi = """!verbose 0
Name "%s"
OutFile "%s"
InstallDir $TEMP
RequestExecutionLevel user
!include "LogicLib.nsh"
!include "WordFunc.nsh"
!include "FileFunc.nsh"
SilentInstall silent
SetCompressor LZMA
Section ""
  SetOutPath $INSTDIR
  File /r "%s"
SectionEnd
Function .onInstSuccess
  ${If} $INSTDIR == $TEMP
    ${GetParameters} $R0
    ExecWait '"$TEMP\\%s" $R0'
    RMDir /r "$TEMP\\%s"
  ${EndIf}
FunctionEnd
"""
sep_line = "-" * 80
# NSIS script compiler (standard installation location)
makensis = r'"C:\Program Files (x86)\NSIS\makensis.exe"'
# or just this if on path:
makensis = '"makensis.exe" '

try:
    dist = sys.argv[1]
except:
    dist = psg.PopupGetFolder(
        "Select a '.dist' folder:", "Make Nuitka Installation File"
    )

dist = os.path.abspath(dist)
if not os.path.isdir(dist) or not dist.endswith(".dist"):
    raise SystemExit("'%s' is not a Nuitka dist folder" % dist)


dist_base = os.path.basename(dist)  # basename of dist folder
dist_dir = os.path.dirname(dist)  # directory part of dist
exe = dist_base.split(".")[0] + ".exe"
one_file = exe
# finalize installation script
nsi_final = nsi % (
    dist_base,
    os.path.join(dist_dir, one_file),
    dist,
    os.path.join(dist_base, exe),
    dist_base,
)

# put NSIS installation script to a file
nsi_filename = dist + ".nsi"
nsi_file = open(nsi_filename, "w")
nsi_file.write(nsi_final)
nsi_file.close()

t0 = time.time()
rc = sp.Popen(makensis + " " + nsi_filename, shell=True)

print(
    "\nNow executing", makensis, "\nPlease wait, this may take some time.\n", sep_line
)
return_code = rc.wait()

t1 = time.time()
print(
    sep_line,
    "\nOneFile generation return code:",
    return_code,
    "\nDuration: %i sec." % int(round(t1 - t0)),
)
