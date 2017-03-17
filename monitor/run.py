#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import signal
from libs import daemon
from monitor import monitoring

''''https://www.python.org/dev/peps/pep-3143/'''

# sets working directory
workingDir = '/tmp/pymonits'

if not os.path.exists(workingDir):
    os.makedirs(workingDir, 0o755)


def program_cleanup():
    print("cleaning up...")


context = daemon.DaemonContext(
    working_directory=workingDir,
    umask=0o002,
)

context.signal_map = {
    signal.SIGTERM: program_cleanup,
    signal.SIGHUP: 'terminate',
}

with context:
    print('starting damon')
    monitoring.loop()
