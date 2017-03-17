import os
import time
import paramiko
from paramiko import SSHClient
from scp import SCPClient
import urllib.request
from common.operations import Operation


class SSHOperation(Operation):
    '''Base class for common ssh procedures'''

    def __init__(self, args={}):
        self.args = args
        self.scp = None
        self.ssh = None

    def set_ssh(self, ssh):
        self.ssh = ssh

    def set_scp(self, scp):
        self.scp = scp

    def _init_scp(self):
        if self.ssh is None:
            self._init_ssh()
        if self.scp is None:
            self.scp = SCPClient(self.ssh.get_transport())

    def _init_ssh(self):
        if self.ssh is None:
            self.__int_ssh(self.args.get("host"), str(self.args.get("port", 22)), str(self.args.get("user", "root")),
                           str(self.args.get("pass", "")))

    def __int_ssh(self, server, port, user, password):
        self.log("init ssh connection {}@{}:{} pass: {}", user, server, port, password)
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(str(server), int(port), str(user), str(password), timeout=100)
        self.ssh = client

    def cleanup(self):
        if self.scp is not (None):
            self.scp.close()
        if self.ssh is not (None):
            self.ssh.close()
        print('connections closed')


class FreeSpace(SSHOperation):
    """Check if there is some free space"""

    def execute(self):
        self._init_ssh()
        sh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command('df')
        firstLine = False;
        for line in ssh_stdout.read().splitlines():
            self.log(str(line.decode("utf-8")))

            if not (firstLine):
                firstLine = True;
                continue

            fields = line.split()
            percentage = fields[4].decode("utf-8").replace('%', '')
            disk = fields[5].decode("utf-8").replace('%', '')
            left = round(int(fields[3].decode("utf-8").replace('%', '')) / 1000)
            if int(percentage) > 80:
                self.err('{}% space taken on {} ! {} MB left.', percentage, disk, left)
                self._status = self.EXIT_FAILURE

        self._status = self.EXIT_SUCCESS


class Upload(SSHOperation):
    """Upload and unarchive archive to a app directory
    """

    def execute(self):
        """
        Parameters:
          package_archive_path - path to a local archive
          app_dir - destination dir
        """
        src = self.args.get("package_archive_path")
        dest = self.args.get("app_dir")

        if src is None:
            raise Exception("archive path is None!")
        if dest is None:
            raise Exception("dest path is None!")

        self.log('copy {} to {}'.format(str(src), str(dest)))
        ts = str(time.time())
        tmpFileName = '/tmp/paczka' + ts;

        # TODO check free space

        self.log('uploading {} to {}'.format(src, tmpFileName))
        # upload

        self._init_scp()
        self.scp.put(src, tmpFileName)
        # unpack
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command('tar -zxvf ' + tmpFileName + ' -C ' + dest)
        self.log(ssh_stderr)
        self.log(tmpFileName + ' unarchived to ' + dest)
        # TODO verify files

        channel = ssh_stdout.channel
        code = channel.recv_exit_status()

        if code == 0:
            self._status = self.EXIT_SUCCESS
        else:
            self.log("Copy cmd exit code = {}", code)
            self._status = self.EXIT_FAILURE


class Restart(SSHOperation):
    """Restart the tomcat (or other kind of process)"""

    def execute(self):
        """
         Parameters:
           restart_ps_name - command to restart a process
           restart_run_cmd - command to start a process
           restart_stop_cmd - optional, command to stop a process
         """

        ps_name = self.args.get('restart_ps_name');
        run_cmd = self.args.get('restart_run_cmd');
        stop_cmd = self.args.get('restart_stop_cmd');

        if not run_cmd:
            raise Exception("run_cmd path is Empty!")
        if not ps_name:
            raise Exception("ps_name path is Empty!")

        self.log("restarting {} ", ps_name)
        self._init_ssh()
        pids = get_tomcat_pid(self.ssh, ps_name)
        self.log('tomcat has {} running instances ', str(len(pids)))
        # kill if only one instance
        if len(pids) == 1:
            if not stop_cmd:
                stop_cmd = 'kill -9 ' + pids[0]

            max_retries = 3
            retries = 0
            success = False

            while retries < max_retries and not success:
                time.sleep(1)
                retries = retries + 1
                self.log('stopping cmd {}', stop_cmd)
                ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(stop_cmd, timeout=15)
                # check if is dead
                pids = get_tomcat_pid(self.ssh, ps_name);
            success = len(pids) == 0
        elif len(pids) == 0:
            self.log('tomcat instance was not running')
        else:
            self.log('{} tomcat instances still running', str(len(pids)))
            self._status = self.EXIT_FAILURE
            return

        self.log('starting tomcat with command {}', run_cmd)
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(run_cmd, timeout=15);

        self.log(ssh_stderr);
        # wait for output
        timeout = 30
        endtime = time.time() + timeout
        while not ssh_stdout.channel.eof_received:
            time.sleep(1)
            if time.time() > endtime:
                ssh_stdout.channel.close()
                break

        for line in ssh_stdout.read().splitlines():
            self.log(str(line))

        max_retries = 3
        retries = 0
        success = False
        while retries < max_retries and not success:
            time.sleep(1)
            self.log('retry...')
            retries = retries + 1
            pids = get_tomcat_pid(self.ssh, ps_name);
            if len(pids) == 1:
                self.log('tomcat started  ({})', pids[0])
                success = True
            else:
                self._status = self.EXIT_FAILURE
                return

        self._status = self.EXIT_SUCCESS


class UploadAndRestart(SSHOperation):
    """Uploads and restart - open only one connection"""

    def execute(self):

        try:
            self._init_scp()
            upload = Upload(self.args)
            upload.set_ssh(self.ssh)
            upload.set_scp(self.scp)
            upload.execute()

            status = upload.get_status

            if status == Operation.EXIT_SUCCESS:
                self._products = {**self._products, **upload.get_products()}
                self.args = {**self.args, **upload._products}

                restart = Restart(self.args)
                restart.set_ssh(self.ssh)
                restart.set_scp(self.scp)
                restart.execute()
                self._status = restart.get_status
            else:
                self._status = self.EXIT_FAILURE

        except Exception as ex:
            raise Exception(ex)
        finally:
            self.cleanup()


# Utility functions

def get_tomcat_pid(ssh, psname):
    """Try to get pid of a tomcat instance"""
    cmd = 'ps aux | grep ' + psname
    print("cmd: " + cmd)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)

    channel = ssh_stdout.channel
    print("before status")
    status = channel.recv_exit_status()
    print("status: " + str(status))
    pids = []
    for line in ssh_stdout.read().splitlines():
        print(str(line))
        fields = line.strip().split()
        # Array indices start at 0 unlike AWK
        print("fields:")
        # for filed in fields:
        #	print(filed)
        prName = fields[10].decode('UTF-8');
        print('program name : ' + prName)
        if prName == 'grep' or prName == 'bash':
            print('continue...')
            continue
        # append space to process name so it will not match false positives
        if 'tomcat' in psname:
            if 'org.apache.catalina.startup.Bootstrap' in str(line) and (psname + ' ') in str(line):
                fields = line.split()
                pid = fields[1].decode("utf-8")
                pids.append(pid)
                print('match: ' + pid)
        else:
            fields = line.split()
            pid = fields[1].decode("utf-8")
            pids.append(pid)
            print('match: ' + pid)
    return pids


if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    pass
