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
import pytest
import string
import random
import shutil

PIECE_LENGTH1 = 2 ** 14
PIECE_LENGTH2 = 2 ** 16
PIECE_LENGTH3 = 2 ** 18
PIECE_LENGTH4 = 2 ** 19
PIECE_LENGTH5 = 2 ** 20
PIECE_LENGTH6 = 2 ** 22

PIECE_LENGTHS = [
    PIECE_LENGTH1,
    PIECE_LENGTH2,
    PIECE_LENGTH3,
    PIECE_LENGTH4,
    PIECE_LENGTH5,
    PIECE_LENGTH6,
]


class MakeDirError(Exception):
    pass


def write_out_bin(path, exp=25):
    with open(path, "wb") as fd:
        l = list(string.printable)
        while True:
            txt = gen_out(l) + "\n"
            size = len(txt)
            l.append(txt)
            fd.write(txt.encode("utf-8"))
            if size > (2 ** exp):
                break
    return os.path.getsize(path)


def gen_out(l):
    txt = ""
    for i in range(random.randint(25, 35)):
        txt += random.choice(l)
    return txt


def gen_exp(n):
    if n >= 5:
        n = 5
    elif n <= 1:
        n = 1
    sizes = {1: 23, 2: 24, 3: 25, 4: 26, 5: 27}
    return sizes[n]


def gen_name(name):
    current = os.path.dirname(os.path.abspath(__file__))
    fname = os.path.join(current, name)
    return fname


def rmpath(path):
    if not os.path.exists(path):
        return
    elif os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


@pytest.fixture(scope="module")
def testfile(n=1):
    exp = gen_exp(n)
    fname = gen_name("testfile.bin")
    write_out_bin(fname, exp)
    yield fname
    rmpath(fname)


@pytest.fixture(scope="module")
def testdir(n=1):
    exp = gen_exp(n)
    dname = gen_name("testdir")
    rmpath(dname)
    os.mkdir(dname)
    test_structure = {
        "testing": [
            "temp_data.dat",
            "temp_text.txt",
        ],
        "temp_dir": [
            "temp_data.dat",
            "temp_text.txt",
        ],
    }
    for k, v in test_structure.items():
        subdir = os.path.join(dname, k)
        os.mkdir(subdir)
        for fd in v:
            temp1 = os.path.join(subdir, fd)
            write_out_bin(temp1, exp)
    yield dname
    rmpath(dname)
