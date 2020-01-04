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
from buildsourcesCompare import Svn

OUTPUT = '/tmp/buildsourcesCompare/'
SVNREPO = 'svn://ravesvn/Rave'
SVNREL = '/projects/integration/platform/buildsources/'

def test_svn_known_good():
    # svn://ravesvn/Rave/projects/integration/platform/buildsources/g/gcc/gcc-4.9.4/gcc-4.9.4.tar.bz2
    file = "g/gcc/gcc-4.9.4/gcc-4.9.4.tar.bz2"
    result =  Svn(SVNREPO, SVNREL).exists(file)
    assert(True == result)

def test_svn_known_bad():
    file = "g/gcc/gcc-4.9.4/gcc-4.9.8675309.tar.bz2"
    result =  Svn(SVNREPO, SVNREL).exists(file)
    assert(False == result)

def test_svn_list_base():
    result = Svn(SVNREPO, SVNREL).list('')
    for code in range(ord('a'), ord('z') + 1):
        c = chr(code)
        assert(result.get(c) != None)

def test_svn_list_gcc_4p9():
    result = Svn(SVNREPO, SVNREL).list('g/gcc/gcc-4.9.4')
    assert(None != result.get('gcc-4.9.4.tar.bz2'))
    assert(None != result.get('gcc-4.9.4-sh-no-multilib-osdirnames.patch'))
    assert(None != result.get('gcc-4.9.4.tar.bz2.md5sum'))
    assert(None == result.get('gcc-4.9.4'))
    assert(None == result.get('gcc-4.94'))

def test_svn_download_good():
    # svn://ravesvn/Rave/projects/integration/platform/buildsources/g/gcc/gcc-4.9.4/gcc-4.9.4.tar.bz2.md5sum
    svn = Svn(SVNREPO, SVNREL)
    file = 'gcc-4.9.4.tar.bz2.md5sum'
    if not os.path.exists(OUTPUT):
        os.mkdir(OUTPUT)
    assert(os.path.exists(OUTPUT))
    if os.path.exists(OUTPUT + file):
        os.remove(OUTPUT + file)
    svn.download(OUTPUT + 'gcc-4.9.4.tar.bz2.md5sum', 'g/gcc/gcc-4.9.4/' + file)
    assert(os.path.exists(OUTPUT + file))


def test_svn_download_bad():
    # svn://ravesvn/Rave/projects/integration/platform/buildsources/g/gcc/gcc-4.9.4/gcc-4.9.4.tar.bz2.nobody
    svn = Svn(SVNREPO, SVNREL)
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

def test_svn_size_good():
    svn = Svn(SVNREPO, SVNREL)
    file = 'gcc-4.9.4.tar.bz2.md5sum'
    size = -1
    try:
        size = svn.size('g/gcc/gcc-4.9.4/', file)
    except Exception:
        size = -2
    assert(52 == size)
