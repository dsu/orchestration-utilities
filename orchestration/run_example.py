#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

sys.path.append("..")  # Adds higher directory to python modules path.

from ssh_operations import Upload
from ssh_operations import FreeSpace
from ssh_operations import UploadAndRestart
from common.operations import Executor
from common.net import ChekPage
from makepackage import MakePackage
from settings_example import *


def main():
    # List that contains list of projects and list of operations to execute. Each operation has a dictionary that contains
    # configuration for each task
    inv = {
        'an application name':
            [
                (FreeSpace, test_ssh_conf),

            ],
        'another application name':
            [
                (FreeSpace, ssh_conf),
                (MakePackage, pacakaging_conf),
                # For python 3.5 you can merge many dictionaries into one
                (UploadAndRestart, {**ssh_conf, **pacakaging_conf, **restart_conf}),
                # You can create configuration ad-hoc
                (ChekPage, {'app_url': 'http://xyz.xyz/chek-if-i-am-working'})
            ]
    }

    hostKey = 'wiw';
    # select an application and initialize Executor class. It is responsible for executing tasks
    chain = Executor(inv[hostKey])
    # you can also modify operation configuration just before execution:
    chain.arg('MakePackage', 'hours_old_max', 24 * 7)
    # execute operations - one by one. An operation is executed only if previous was successsful.
    chain.all()
    print('finished')


if __name__ == "__main__":
    main()
else:
    pass
