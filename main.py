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

# Bootstrap:
# $ sudo apt install python3-pip pipenv
# $ pipenv install requests svn

from src.http import Http
from src.svn import Svn
from src.workorder import WorkorderFilter
import hashlib, os, argparse, logging, shutil, sys
from enum import Enum

log = logging.getLogger('buildsourcesCompare')

class Result(object):
    def __init__(self, detail):
        self.detail = detail
class ResultMatch(Result):
    def __init__(self):
        super(ResultMatch, self).__init__(None)
class ResultNotInHttp(Result):
    def __init__(self, detail = None):
        super(ResultNotInHttp, self).__init__(detail)
class ResultSizeDiff(Result):
    def __init__(self, detail = None):
        super(ResultSizeDiff, self).__init__(detail)
class ResultHashDiff(Result):
    def __init__(self, detail = None):
        super(ResultHashDiff, self).__init__(detail)
class ResultHashSkip(Result):
    def __init__(self, detail = None):
        super(ResultHashSkip, self).__init__(detail)

def download(http, svn, tmp, path, file):
    localsvn = tmp + path + file + '.svn'
    localhttp = tmp + path + file + '.http'
    if not os.path.exists(tmp + path):
        os.makedirs(tmp + path)
    if not os.path.exists(localsvn):
        svn.download(localsvn, path + file)
    if not os.path.exists(localhttp):
        http.download(localhttp, path + file)
    return (localhttp, localsvn)

class Comparison(object):
    def __init__(self, http, svn, tmp, path, file):
        self.result = None
        self.http = http
        self.svn = svn
        self.tmp = tmp
        self.path = path
        self.file = file
    def __call__(self):
        raise Exception

class HttpExists(Comparison):
    def __init__(self, http, svn, tmp, path, file):
        super(HttpExists, self).__init__(http, svn, tmp, path, file)
    def __call__(self):
        if self.http.exists(self.path + self.file):
            return ResultMatch()
        return ResultNotInHttp()

class SizeDiff(Comparison):
    def __init__(self, http, svn, tmp, path, file):
        super(SizeDiff, self).__init__(http, svn, tmp, path, file)
    def __call__(self):
        svnsz = self.svn.size(self.path, self.file)
        htsz = self.http.size(self.path, self.file)
        msg='httpsz={}, svnsz={}'.format(htsz, svnsz)
        log.debug('{}: {}'.format(self.path + self.file, msg))
        if svnsz == htsz:
            return ResultMatch()
        download (self.http, self.svn, self.tmp, self.path, self.file)
        return ResultSizeDiff(msg)

class HashDiff(Comparison):
    def __init__(self, http, svn, tmp, path, file):
        super(HashDiff, self).__init__(http, svn, tmp, path, file)
    def __call__(self):
        def md5(file):
            md5 = hashlib.md5()
            with open(file, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5.update(chunk)
            return md5.hexdigest()
        skip = [ 'tar', 'xz', 'tgz', 'gz', 'zip', 'bz2' ]
        for c in skip:
            if -1 != self.file.find(c):
                msg = "skip md5 for tarball {}".format(c)
                log.debug('{}: {}'.format(self.path + self.file, msg))
                return ResultHashSkip(msg)

        httplocal = self.tmp + self.file + '.http'
        svnlocal = self.tmp + self.file + '.svn'
        if os.path.exists(httplocal):
            raise Exception
        if os.path.exists(svnlocal):
            raise Exception
        (httplocal, svnlocal) = download(self.http, self.svn, self.tmp, self.path, self.file)
        svnmd5 = md5(svnlocal)
        htmd5 = md5(httplocal)
        msg = 'httpmd5={}, svnmd5={}'.format(htmd5, svnmd5)
        log.debug('{}: {}'.format(self.path + self.file, msg))
        if htmd5 == svnmd5:
            return ResultMatch()
        return ResultHashDiff(msg)

def postResult(reportfile, result, path, file):
    l = log.critical
    if isinstance(result, ResultMatch) or isinstance(result, ResultHashSkip):
        l = log.info
        reportfile = None
    msg = '{}: {}'.format(type(result).__name__, path + file)
    if None != result.detail:
        msg += ': {}'.format(result.detail)
    l(msg)
    if None != reportfile:
        reportfile.write(msg + '\n')
        reportfile.flush()

def dfs(http, svn, tmp, reportfile, path):
    log.warning("exploring {}".format(path))
    list = svn.list(path)
    for k in list.keys():
        pathToK = path + k
        if False == list[k]['is_directory']:
            comparators = [ HttpExists, SizeDiff, HashDiff ]
            result = None
            for c in comparators:
                result = c(http, svn, tmp, path, k)()
                if not isinstance(result, ResultMatch) and not isinstance(result, ResultHashSkip):
                    break
            postResult(reportfile, result, path, k)
        else:
            dfs(http, svn, tmp, reportfile, pathToK + '/')

def main():
    parser = argparse.ArgumentParser(
        description = 'Aggregate all in-use packages across workorders. For each such package, ensure that buildsources contains no proprietary modifications to tarballs, patches, etc. Identify exceptions.'
        )
    parser.add_argument('-s', '--svnrepo',
        help='The SVN repository to use as source (default: %(default)s)',
        default='svn://ravesvn.ims.dom/Rave')
    parser.add_argument('-c', '--configpath',
        help="The relative path in the SVN repository to use for fetching workorders (default: %(default)s)",
        default='/projects/integration/platform/OS/factory/src/local/config/')
    parser.add_argument('-r', '--svnrelpath',
        help="The relative path in the SVN repository to use for buildsources source (default: %(default)s)",
        default='/projects/integration/platform/buildsources/')
    parser.add_argument('-t', '--httprepo',
        help='The HTTP repository & relative path to use as comparison target (default: %(default)s)',
        default='http://repository.timesys.com/buildsources/')
    parser.add_argument('-o', '--reportfile',
        help='A full path to a file to write a report to (default=%(default)s)',
        default='/tmp/buildsourcesCompare-report')
    parser.add_argument('-l', '--logfile',
        help='A full path to a file to write a log at DEBUG to (default=%(default)s)',
        default='/tmp/buildsourcesCompare-log')
    parser.add_argument("-v", "--verbosity",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Console verbosity level (default: %(default)s)",
        default='ERROR')
    parser.add_argument('-p', '--tmppath',
        help='The temporary path to use for operations (default: %(default)s)',
        default='/tmp/buildsourcesCompare/')

    formatter = logging.Formatter(fmt='%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s',
            datefmt='%Y/%m/%d %H:%M:%S') # %I:%M:%S %p AM|PM format
    args = parser.parse_args()

    reportfile = args.reportfile
    logfile = args.logfile
    count = 0
    while os.path.exists(reportfile) or os.path.exists(logfile):
        count = count + 1
        reportfile = args.reportfile + '.' + str(count)
        logfile = args.logfile + '.' + str(count)
    report = open(reportfile, "w+")

    if os.path.exists(args.tmppath):
        shutil.rmtree(args.tmppath)
    os.mkdir(args.tmppath)

    log.setLevel(logging.DEBUG)

    fh = logging.FileHandler(logfile)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.getLevelName(args.verbosity))
    ch.setFormatter(formatter)
    log.addHandler(ch)

    log.info("Creating report at {}".format(reportfile))
    log.info("Creating log at {}".format(logfile))

    svn = Svn(repo=args.svnrepo, path=args.svnrelpath)
    woSvn = Svn(repo=args.svnrepo, path=args.configpath)
    http = Http(baseurl=args.httprepo)

    woFilter = WorkorderFilter(args.tmppath, woSvn)
    for v in woFilter.pkgs():
        dfs(
            http=http,
            svn=svn,
            tmp = args.tmppath,
            reportfile=report,
            path=v + '/')


if __name__ == "__main__":
    main()
