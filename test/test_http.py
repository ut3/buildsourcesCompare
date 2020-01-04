# Copyright (c) 2018, J. Rick Ramstetter
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
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

import sys, os
sys.path.insert(0, os.path.abspath('..'))

import pytest
from buildsourcesCompare import Http # pylint disable=no-name-in-module

OUTPUT = '/tmp/buildsourcesCompare'
TIMESYS = 'http://repository.timesys.com/buildsources/'

def test_timesys_known_good():
    # http://repository.timesys.com/buildsources/g/gcc/gcc-8.3.0/gcc-8.3.0.tar.xz
    file = "g/gcc/gcc-8.3.0/gcc-8.3.0.tar.xz"
    result =  Http(TIMESYS).exists(file)
    assert(True == result)

def test_timesys_known_bad():
    # http://repository.timesys.com/buildsources/g/gcc/gcc-8.3.0/gcc-8675309.tar.xz
    file = "g/gcc/gcc-8.3.0/gcc-8675309.tar.xz"
    assert(False == Http(TIMESYS).exists(file))


def test_timesys_download_good():
    # svn://ravesvn/Rave/projects/integration/platform/buildsources/g/gcc/gcc-4.9.4/gcc-4.9.4.tar.bz2.md5sum
    svn = Http(TIMESYS)
    file = 'gcc-4.9.4.tar.bz2.md5sum'
    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT)
    assert(os.path.exists(OUTPUT))
    if os.path.exists(OUTPUT + file):
        os.remove(OUTPUT + file)
    svn.download(OUTPUT + 'gcc-4.9.4.tar.bz2.md5sum', 'g/gcc/gcc-4.9.4/' + file)
    assert(os.path.exists(OUTPUT + file))


def test_timesys_download_bad():
    # svn://ravesvn/Rave/projects/integration/platform/buildsources/g/gcc/gcc-4.9.4/gcc-4.9.4.tar.bz2.nobody
    svn = Http(TIMESYS)
    file = 'gcc-4.9.4.tar.bz2.nobody'
    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT)
    assert(os.path.exists(OUTPUT))
    if os.path.exists(OUTPUT + file):
        os.remove(OUTPUT + file)
    caught = False
    try:
        svn.download(OUTPUT + file, 'g/gcc/gcc-4.9.4' + file)
    except Exception:
        caught = True
    assert(caught == True)

def test_timesys_size_good():
    ts = Http(TIMESYS)
    file = 'gcc-4.9.4.tar.bz2.md5sum'
    size = -1
    try:
        size = ts.size('g/gcc/gcc-4.9.4/', file)
    except Exception:
        size = -2
    assert(52 == size)