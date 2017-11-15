Python 3.5 orchestration utilities
==============================

Tools useful when developing small or medium scale web applications.
Specifically it is only used for Java web app running on Tomcat and
Linux. You can create own tasks by extending commons.Operation class or
you can excute any function. You can put operations and function to a
chain of execution. It doesn\'t try to replace Ansible, Chef or other
tools but it is more convenient - there is no configuration file. You
can configure functions you want to have any way you want. You can
execute any function, you don\'t need to follow any specified interface.
Generally, a bunch of utilities is more convenient than the whole
framework and Python is a great environment for that.

orchestration module
====================

It is supposed to run locally on a developer machine. paramiko (pip
install paramiko) and [scp] (pip install scp) is required. Also watchdog
can be needed (pip install watchdog) for execute phases on a file
change. Can prepare archive and upload java and other files to the
server via ssh. It can upload files that are newer than x hours. It can
check if .class files are in specified java version. You can send
yourself an e-mail when a web app stops responding (You can use
mail\_example.py)

An example of usage is in run\_example.py file.

For example to send files to the server, restart serwer and check if application responds on given addres you can run main.py as follows.
```python
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
```
Settings can be stored in a separate file as below.

```python
example_ssh = {'host': '10.10.10.1',
           'user': 'user',
           'sudo': True,
           'pass': 'xyz'}         


example_package = {
    'jversion': 1.8,
    'dir_src': '/data/workspaces/classes/',
    'compress': False,
    'dir_dst': '/data/package',
    'arch_file_dst': '/data/package',
    'dir_exclude': r"(.*pdf/conf.*|.*WEB-INF/logs.*|.*buffer/.*|.*files/.*|.*properties)",
    'hours_old_max': 1 * 1 * 8,
    'app_dir': '/var/www1/bw2/WEB-INF/classes',
}

example_restart = {
    'restart_stop_cmd': 'systemctl stop tomcat7',
    'restart_ps_name': '/usr/lib/jvm/java-8-oracle/bin/java',
    'restart_run_cmd': 'systemctl start tomcat7',
    'sudo': True
}
```

monitor module
==============

It is supposed to run on server. Contains some tools for checking if a
web app is still running and tries to restart app when a problem occurs.
It also can gather some diagnostic information from specified log files.
Nothing fancy but it seems easier and more flexible than any other tool
I have tested.

An example of usage is in run\_example.py file.

simple\_web\_console
====================

Proof of concept based on Tornado (required). If you want a Linux
console available for a web page use [butterfly] - It is awesome.

  [scp]: https://github.com/jbardin/scp.py
  [butterfly]: https://github.com/paradoxxxzero/butterfly