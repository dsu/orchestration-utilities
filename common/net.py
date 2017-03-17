#!/usr/bin/python
# -*- coding: utf-8 -*-


import urllib
import time
from common.operations import Operation


def check_is_page_ok(url):
    """Check if web page is responding"""
    print('connecting to {} ...'.format(url))
    url_readed = False
    max_retries = 5
    retries = 0
    sleepSec = 5

    while retries < max_retries and not (url_readed):
        try:
            # xml = urllib.request.urlopen(url).read()
            urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            # Return code error (e.g. 404, 501, ...)
            print('http error status code for {} is {} ({}/{})'.format(url, e.code, retries, max_retries))
            time.sleep(sleepSec)
        except urllib.error.URLError as e:
            # Not an HTTP-specific error (e.g. connection refused)
            print('connection error {} ({}/{})'.format(url, retries, max_retries))
            time.sleep(sleepSec)
        else:
            # 200
            print("Connection OK")
            url_readed = True
        retries = retries + 1
    return url_readed


class ChekPage(Operation):
    def __init__(self, args={}):
        print('ChekPage {} '.format(args))
        self.args = args

    def execute(self):
        url = self.args.get("app_url")
        if not url:
            raise Exception("URL is Empty!")

        if check_is_page_ok(url):
            self._status = self.EXIT_SUCCESS
        else:
            self._status = self.EXIT_FAILURE
