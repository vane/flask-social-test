#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Michal Szczepanski'

import urllib2
import os
import json
import logging

logger = logging.getLogger()


def get_file(url, out):
    u = urllib2.urlopen(url)
    f = open(out, 'wb')
    while True:
        buf = u.read(4096)
        if not buf:
            break
        f.write(buf)
    f.close()


def dir_exist(path):
    if not os.path.exists(path):
        os.makedirs(path)


def file_exist(path):
    if not os.path.isfile(path):
        return False
    return True


def download_libs(path, data):
    for lib in data:
        src = lib['src']
        dst = path+'/'+lib['name']+'/'+src['version']
        for f in src['files']:
            url = src['url']+'/'+src['version']+'/'+f
            a = f.split('/')
            if len(a) > 1:
                sub = '/'.join(a[:1])
            else:
                sub = ''
            out = dst+'/'+f
            dir_exist(dst+'/'+sub)
            if not file_exist(out):
                logger.debug('downloading file : %s , url : %s' % (out, url))
                get_file(url, out)
            else:
                logger.info('skipping file : %s' % url)


def download(path, f):
    data = json.load(open(f, 'r'))
    download_libs(path, data)
