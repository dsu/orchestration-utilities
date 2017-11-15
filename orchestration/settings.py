#!/usr/bin/python
# -*- coding: utf-8 -*-



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
