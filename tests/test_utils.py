#! /usr/bin/python3
# -*- coding: utf-8 -*-

#####################################################################
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#####################################################################

import random
import os
import math
from tests.context import TEST_DIR
from torrentfile.utils import ( path_stat,
                                path_size,
                                get_piece_length,
                                get_file_list,
                                dir_files_sizes)

KIB = 2**10
MIB = KIB**2
GIB = KIB**3
MIN_BLOCK = 2 ** 14
MAX_BLOCK = MIB * 16


class TestUtils:

    def test_get_piece_length(self):
        for i in range(MIB,20*GIB,200 * MIB):
            result = get_piece_length(i)
            total_pieces = math.ceil(i / result)
            assert total_pieces > 20
            assert result % 1024 == 0
            assert math.log2(result) % 1 == 0
            assert result >= MIN_BLOCK
            assert result <= MAX_BLOCK

    def test_path_size(self):
        def walk(path):
            if os.path.isfile(path):
                return []
            sizes = []
            if os.path.isdir(path):
                for item in os.listdir(path):
                    full = os.path.join(path,item)
                    sizes.append(path_size(path))
                    sizes.extend(walk(full))
            return sizes
        path = TEST_DIR
        for size in walk(path):
            assert size > 0

    def test_get_file_list(self):
        results = get_file_list(TEST_DIR)
        assert len(results) > 0

    def test_dir_file_sizes(self):
        filelist, total = dir_files_sizes(TEST_DIR)
        assert len(filelist) > 0
        assert total > 0

    def test_path_stat(self):
        filelist, size, piece_length = path_stat(TEST_DIR)
        assert len(filelist) > 0
        assert size > 0
        assert piece_length > 0
        assert piece_length >= MIN_BLOCK
        assert piece_length <= MAX_BLOCK
        assert math.log2(piece_length) % 1 == 0
        assert piece_length % 1024 == 0
