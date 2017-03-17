import subprocess

from libs.sarge import run, Capture


def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')


def run_cmd(command):
    p = run(command, stdout=Capture())
    out = p.stdout.text
    return out;


if __name__ == '__main__':
    print(run_cmd('top'))  # test
