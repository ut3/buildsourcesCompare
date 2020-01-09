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

import urllib.request as request
import logging, os

log = logging.getLogger('buildsourcesCompare')
sizecache = {}
existscache = {}

class Http(object):
    def __init__(self, baseurl):
        self.baseurl = baseurl

    def exists(self, file):
        url = self.baseurl + file
        if url in existscache:
            log.debug('{}: cached, exists={}'.format(url, str(existscache[url])))
            return existscache[url]
        try:
            response = request.urlopen(url, timeout = 3)
            if response.getcode() == 200:
                log.debug('{}: non-cached, exists=True'.format(url))
                existscache[url] = True
                return True
        except Exception:
            pass
        log.debug('{}: non-cached, exists=False'.format(url))
        existscache[url] = False
        return False

    def list(self):
        assert(False)

    def download(self, outputFile, file):
        url = self.baseurl + file
        log.debug("{}: export to {}".format(url, outputFile))
        request.urlretrieve(url, outputFile + '.http-tmp')
        os.rename(outputFile + '.http-tmp', outputFile)

    def size(self, path, file):
        url = self.baseurl + path + file
        if url in sizecache:
            log.debug('{}: return cached size of {}'.format(url, sizecache[url]))
            return sizecache[url]
        response = {}
        try:
            response = request.urlopen(url, timeout = 3)
        except Exception as e:
            print("Exception web.size(): {}".format(e))
            return -100
        sizecache[url] = response.length
        log.debug('{}: return non-cached size of {}'.format(url, response.length))
        return response.length