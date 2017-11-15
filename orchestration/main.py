#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os
print(os.path.dirname(os.path.realpath(__file__)))
print(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))

sys.path.append("../")

from orchestration.ssh_operations import Upload
from orchestration.ssh_operations import FreeSpace
from orchestration.ssh_operations import UploadAndRestart
from common.operations import Executor
from common.net import ChekPage
from orchestration.makepackage import MakePackage
from orchestration.settings import *

def main():


    inv = {
         'example':
            [
                (MakePackage, { **example_package, **{'dir_exclude': r"(.*pdf/conf.*|.*WEB-INF/logs.*|.*buffer/.*|.*files/.*|.*properties|.*poolman.xml|./.*|.*lucene/.*)" },}),
                (UploadAndRestart, { 'package_archive_path': '/data/package.tar.gz', **example_package,  **example_ssh, **example_restart}),
                (ChekPage,{'app_url': 'http:/10.10.10.30/index'})
            ],
        'example2':
            [   
                (MakePackage, { **mmp_package})
               
            ]
    }

    hostKey = 'example'; #select dictionary
    chain = Executor(inv[hostKey])
    chain.all()
    #chain.watch('/home/dsu/tmp/')
    print('finished')

if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    main()
else:
    pass
