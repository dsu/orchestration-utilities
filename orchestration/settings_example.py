#!/usr/bin/python
# -*- coding: utf-8 -*-

test_ssh_conf = {'host': 'xyz.com',
                 'port': 22,
                 'user': 'root',
                 'pass': 'passsss123'}

ssh_conf = {'host': 'abc.com',
            'port': 220,
            'user': 'user',
            'pass': 'user'}

package_conf = {
    'jversion': 1.6,
    'dir_src': '/data/webapps/app',
    'compress': False,
    'dir_dst': '/data/package',
    'arch_file_dst': '/data/package',
    'dir_exclude': r"(.*pdf/conf.*|.*WEB-INF/logs.*|.*buffer/.*|.*files/.*)",
    'hours_old_max': 1 * 3,
    'app_dir': '/var/www1/app',
}

restart_conf = {
    'restart_stop_cmd': 'systemctl stop tomcat7',
    'restart_ps_name': '/usr/lib/jvm/java-7-oracle/bin/java',
    'restart_run_cmd': 'systemctl start tomcat7',
}
