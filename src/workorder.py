# Copyright (c) 2020, J. Rick Ramstetter
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

import logging, os


class WorkorderFilter(object):
    def __init__(self, tmp, svn):
        self.workorderPath = os.path.join(tmp, 'workorders')
        self.packages = []
        svn.download(self.workorderPath, '')
        list = os.listdir(self.workorderPath)
        for item in list:
            if not item.endswith('.config'):
                os.remove(os.path.join(self.workorderPath, item))
                os.sync()
            elif -1 != item.find('uboot'):
                os.remove(os.path.join(self.workorderPath, item))
                os.sync()
        self.extract_packages()

    def pkgs(self):
        for v in self.packages:
            yield v

    def extract_packages(self):
        list = os.listdir(self.workorderPath)
        for item in list:
            with open(os.path.join(self.workorderPath, item), 'r') as f:
                lastline = None
                for l in f:
                    if False == l.startswith('TSWO_'):
                        continue
                    if -1 != l.find('_REVISION='):
                        continue

                    if None != lastline and -1 != lastline.find('_VERSION=') and -1 != l.find('_URL='):
                        u = self.extractUrl(l)
                        v = self.extractVersion(lastline)
                        self.packages.append( (u + v).strip() )
                        lastline = None
                    lastline = l

    def extractVersion(self, line):
        splitOnEqual=line.split('=')
        # [0]: TSWO_package_VERSION=
        # [1]: "1.2.3"
        return splitOnEqual[1].replace('"', '')

    def extractUrl(self, line):
        splitOnEqual=line.split('=')
        url=splitOnEqual[1].replace('"','')
        url=url.replace('$(TSWO_GLOBAL_SOURCE_LOCATION)/', '')
        url=url.split('$')[0]
        return url