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

# The pypi 'svn' package is causing lint errors that I don't care to investigate.
import svn.remote # pylint: disable=import-error,no-name-in-module
import logging

log = logging.getLogger('buildsourcesCompare')

class Svn:
    def __init__(self, repo, path):
        self.repo = repo
        self.path = path
        self.c = svn.remote.RemoteClient(self.repo) # pylint: disable=no-member

    def exists(self, file):
        path = self.path + file
        try:
            self.c.info(rel_path = path)
            log.debug('{}: exists'.format(path))
            return True
        except Exception as e:
            print("svn.exists exception {}".format(e))
        log.debug('{}: does not exist'.format(path))
        return False

    def download(self, outputFile, file):
        # Can't use the self.c client because path is fixed
        log.debug('{}: export to {}'.format(self.repo + self.path + file, outputFile))
        c = svn.remote.RemoteClient(self.repo + self.path + file) # pylint: disable=no-member
        c.export(outputFile)

    def list(self, p = ''):
        if p is '':
            p = self.path
        else:
            p = self.path + p
        data = {}
        try:
            data = self.c.list(extended = True, rel_path = p)
        except Exception as e:
            print("svn.list exception (svn) {}".format(e))
            return {}
        dict = {}
        for d in data:
            name = d.pop('name')
            dict[name] = d
        return dict

    def size(self, path, file):
        data = self.list(path + file)
        if data[file]['is_directory'] == True:
            raise Exception
        return data[file]['size']