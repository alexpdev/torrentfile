import os
import pytest
import random
import string
import shutil
from torrentfile import main


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


@pytest.fixture(scope="module")
def testfile(n=1):
    if n > 5:
        n = 5
    elif n < 1:
        n = 1
    sizes = {1: 23, 2: 24, 3: 25, 4: 26, 5: 27}
    current = os.path.dirname(os.path.abspath(__file__))
    fname = os.path.join(current, "testfile.bin")
    write_out_bin(fname, sizes[n])
    yield fname
    os.remove(fname)


@pytest.fixture(scope="module")
def testdir(n=1):
    if n > 5:
        n = 5
    elif n < 1:
        n = 1
    sizes = {1: 23, 2: 24, 3: 25, 4: 26, 5: 27}
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
    current = os.path.dirname(os.path.abspath(__file__))
    dname = os.path.join(current, "testdir")
    os.mkdir(dname)
    for k, v in test_structure.items():
        subdir = os.path.join(dname, k)
        os.mkdir(subdir)
        for fd in v:
            temp1 = os.path.join(subdir, fd)
            write_out_bin(temp1, sizes[n])
    yield dname
    shutil.rmtree(dname)


"""
Options = [
    "--created-by",
    "--comment",
    "-o",
    "--path",
    "--piece-length",
    "--private",
    "--source",
    "-t"
]
"""


def test_cli_no_args():
    with pytest.raises(Exception) as excp:
        args = []
        assert not main(args)
