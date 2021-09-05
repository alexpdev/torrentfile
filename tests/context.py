#! /usr/bin/python3
# -*- coding: utf-8 -*-

#####################################################################
# THE SOFTWARE IS PROVIDED AS IS WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#####################################################################

import os
import shutil
import string

TD = os.path.abspath(os.path.dirname(__file__))

class MakeDirError(Exception):
    pass

def fill_file(path, exp):
    bits = (string.printable).encode('utf8')
    l = len(bits)
    with open(path, "wd") as fd:
        while l < 2**exp:
            fd.write(bits)
    return

def fill_folder(folder):
    files = {"file1.bin": 26, "file2.bin": 27, "file3.bin": 28}
    for k,v in files.items():
        path = os.path.join(folder, k)
        fill_file(path, v)
    return

def rmpath(path):
    if not os.path.exists(path): return
    if os.path.isdir(path): shutil.rmtree(path)
    else: os.remove(path)
    return
