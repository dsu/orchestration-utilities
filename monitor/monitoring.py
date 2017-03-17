#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import glob
import logging
import os
import time
from logging.handlers import RotatingFileHandler

import psutil

from common.net import check_is_page_ok
from libs.sarge import run
from monitor.settings import *

loopSleep = loopSleep or 120
logFilePatterns = logFilePatterns or ()


def create_rotating_log(path, tag):
    """
    Creates a rotating log
    """
    logger = logging.getLogger(tag)
    logger.setLevel(logging.INFO)

    # add a rotating handler
    handler = RotatingFileHandler(path, maxBytes=1000 * 1000 * 10,
                                  backupCount=2)

    formatter = logging.Formatter(
        '%(asctime)s orch_tools [%(process)d]: %(message)s',
        '%b %d %H:%M:%S')
    # formatter.converter = time.gmtime  # if you want UTC time
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


def create_plain_rotating_log(path, tag):
    """
    Creates a rotating log
    """
    logger = logging.getLogger(tag)
    logger.setLevel(logging.INFO)
    # add a rotating handler
    handler = RotatingFileHandler(path, maxBytes=1000 * 1000 * 10,
                                  backupCount=2)
    logger.addHandler(handler)
    return logger


# http://sarge.readthedocs.io/en/latest/overview.html#why-not-just-use-subprocess
log = create_rotating_log('tools.log', 'tools')


def getProcByCmd(cmd, safe):
    count = 0
    ps = None
    if safe:
        cmd = cmd + ' '  # ads space for safety
    for p in psutil.process_iter():
        # print('')
        if any(cmd in pscmd for pscmd in p.cmdline()):
            log.info(
                'PID found: {} {} {}'.format(str(datetime.datetime.fromtimestamp(p.create_time())), str(p.username()),
                                             str(p.cmdline())))
            ps = p
            count = count + 1
    if count == 1:
        return ps
    if count == 0:
        log.warning('There is no process running')
        return None
    else:
        log.error('There are too many processes running ({}) ! '.format(count))
        return None


def kill(name):
    max_retries = 5
    retries = 0
    success = False

    p = getProcByCmd(name, False);
    if p == None:
        log.info("No process found with query : {}".format(name))
        return True

    while retries < max_retries and not success:
        retries = retries + 1

        log.info('Terminating {}'.format(p))
        p.terminate()

        try:
            p.kill()
        except psutil.NoSuchProcess as e:
            log.info('Process is already dead')
        p = getProcByCmd(name, False);
        if p == None:
            success = True
            return True
        time.sleep(10)


def retry(fun, funArg, successFun, succArg, params={}):
    success = False
    retries = 0
    max_retries = params.get("max_retries", 5)
    sleepSec = params.get("sleep", 15)
    retrySleep = params.get("retry_sleep", 15)

    while retries < max_retries and not success:
        retries = retries + 1
        log.info('trying for the {} time'.format(retries))
        log.info('execute function with arg : {}'.format(funArg))
        fun(funArg)

        if sleepSec > 0:
            time.sleep(sleepSec)

        success = successFun(succArg)
        log.info('success check : {} with arg {}'.format(success, succArg))

        if success:
            return True
        else:
            if retrySleep > 0:
                time.sleep(retrySleep)

    return success


def startSrv(cmd, pageUrl):
    return retry(lambda cmdarg: run(cmdarg, async=True), cmd, lambda pageUrl: check_is_page_ok(pageUrl), pageUrl)


def loop():
    log.info("loop starts ...")
    while True:
        if not check_is_page_ok(pageUrl):
            try:
                dumpTop()
                dumpLogs()
                dumpLastModified()
            except Exception as e:
                log.warning(e)
            print('killing ...')
            kill(killPsWith);
            print('starting ...')
            started = startSrv(startCmd, pageUrl)
            if started:
                log.info('Started')
            else:
                log.error('Staring error!')
        time.sleep(loopSleep)


def prepareDumps():
    if not os.path.exists('dumps'):
        os.makedirs('dumps')


def dumpTop():
    prepareDumps()
    now = datetime.datetime.today().strftime("%Y.%m.%d_%H.%M.%S")
    with open(os.path.join('dumps', "top_" + now + ".log"), "w") as outfile:
        run('/bin/top -n1', stdout=outfile)


def dumpLogs():
    prepareDumps()
    now = datetime.datetime.today().strftime("%Y.%m.%d_%H.%M.%S")

    for fileName in logFiles:
        baseName = os.path.basename(fileName)
        try:
            with open(os.path.join('dumps', baseName + "_" + now + ".log"), "w") as outfile:
                run('/bin/tail -500 ' + fileName, stdout=outfile)
                print(outfile.name + ' has been saved')
        except Exception as e:
            log.warning(e)


def dumpLastModified():
    prepareDumps()
    now = datetime.datetime.today().strftime("%Y.%m.%d_%H.%M.%S")

    for pattern in logFilePatterns:
        print('find for files by pattern: ' + pattern)
        try:
            fileName = max(glob.iglob(pattern), key=os.path.getctime)
            print('last modified file: {}'.format(fileName))
            if fileName != None:
                baseName = os.path.basename(fileName)
                with open(os.path.join('dumps', baseName + "_" + now + ".log"), "w") as outfile:
                    run('/bin/tail -500 ' + fileName, stdout=outfile)
                    print(outfile.name + ' has been saved')
        except Exception as e:
            log.warning(e)
