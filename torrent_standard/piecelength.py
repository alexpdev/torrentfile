#! /usr/bin/python3
# -*- coding: utf-8 -*-

###############################################################################
# BSD 2-Clause License
#
# Copyright (c) 2021, AlexpDev
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###############################################################################

import math

Kb = 2**10
Mb = Kb**2
Gb = Kb**3

__all__ = ["get_piece_length"]

def get_piece_length(size):
    """
    Calculate the ideal piece length for bittorrent data.

    Args:
        size (int): total bits of all files incluided in .torrent file

    Returns:
        int: the ideal peace length calculated from the size arguement
    """
    length = size / 1500  # 1500 = ideal number of pieces

    # Check if length is under minimum 16Kb
    if length < 16*Kb:
        return 16*Kb

    # Calculate closest perfect power of 2 to target length
    exp = int(math.ceil(math.log2(length)))

    # Check if length is over maximum 8Mb
    if 1 << exp > 8 * Mb:
        return 8 * Mb

    # Ensure total pieces is over 1000
    if size / (2 ** exp) < 1000:
        return 2 ** (exp-1)
    else:
        return 2 ** exp
