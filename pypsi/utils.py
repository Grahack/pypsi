#
# Copyright (c) 2014, Adam Meily
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
#
# * Neither the name of the {organization} nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

'''
Utility functions and classes.
'''

from chardet.universaldetector import UniversalDetector
import codecs
import sys
import threading


class Pipe(object):

    def __init__(self, input=None, output=None):
        if input and output:
            self.input, self.output = input, output
        else:
            fi, fi = os.pipe()
            self.input = os.fdopen(fi, 'r')
            self.output = os.fdopen(fo, 'w')

    def close(self):
        self.input.close()
        self.output.close()


def close_input_pipe(pipe):
    if isinstance(pipe, Pipe):
        pipe.input.close()
    elif pipe:
        pipe.close()

def close_output_pipe(pipe):
    if isinstance(pipe, Pipe):
        pipe.output.close()
    elif pipe:
        pipe.close()


class ThreadLocalProxy(object):

    def __init__(self, obj):
        self._proxies = {}
        self._add_proxy(obj)

    def _add_proxy(self, obj, tid=None):
        tid = tid or threading.get_ident()
        self._proxies[tid] = obj

    def _remove_proxy(self, tid=None):
        tid = tid or threading.get_ident()
        del self._proxies[tid]

    def _get(self, tid=None):
        tid = tid or threading.get_ident()
        return self._proxies[tid]

    def __getattr__(self, name):
        return getattr(self._proxies[threading.get_ident()], name)

    def __setattr__(self, name, value):
        if name in ('_proxies',):
            super(ThreadLocalProxy, self).__setattr__(name, value)
        else:
            setattr(self._proxies[threading.get_ident()], name, value)


def safe_open(path, mode='r'):
    '''
    Retrieves a file's encoding and returns the opened file. If the opened file
    begins with a BOM, it is read before the file object is returned. This
    allows callers to not have to handle BOMs of files.

    :param str path: file path to open
    :param str mode: the mode to open the file (see :func:`open`)
    :returns file: the opened file object
    '''
    u = UniversalDetector()
    first = None
    with open(path, 'rb') as fp:
        bin = first = fp.read(0x1000)

        while not u.done and bin:
            u.feed(bin)
            if not u.done:
                bin = fp.read(0x1000)
    u.close()

    if not first:
        return open(path, mode)

    fp = codecs.open(path, mode, encoding=u.result['encoding'])
    for bom in (codecs.BOM_UTF32_BE, codecs.BOM_UTF32_LE, codecs.BOM_UTF8,
                codecs.BOM_UTF16_BE, codecs.BOM_UTF16_LE):
        if first.startswith(bom):
            fp.seek(len(bom))
            break

    return fp


