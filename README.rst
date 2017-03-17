Python 3.5 orchestration utilities
==============================
Tools useful when developing small or medium scale web applications. Specifically it is only used for Java web app running on Tomcat and Linux. You can create own tasks by extending commons.Operation class or you can excute any function. You can put operations and function to a chain of execution.
It doesn't try to replace Ansible, Chef or other tools but it is more convenient - there is no configuration file. You can configure functions you want to have any way you want. You can execute any function, you don't need to follow any specified interface. Generally, a bunch of utilities is more convenient than the whole framework and Python is a great environment for that.
********************
orchestration module
********************
It is supposed to run locally on a developer machine. paramiko (pip install paramiko) and `scp <https://github.com/jbardin/scp.py>`_  (pip install scp) is required.
Can prepare archive and upload java and other files to the server via ssh.
It can upload files that are newer than x hours.
It can check if .class files are in specified java version.
You can send yourself an e-mail when a web app stops responding (You can use mail_example.py)

An example of usage is in run_example.py file.

***************
monitor module
***************
It is supposed to run on server.
Contains some tools for checking if a web app is still running and tries to restart app when a problem occurs. It also can gather some diagnostic information from specified log files. Nothing fancy but it seems easier and more flexible than any other tool I have tested.

An example of usage is in run_example.py file.

******************
simple_web_console
******************
Proof of concept based on Torenado (required). If you want a Linux console available for a web page use `butterfly <https://github.com/paradoxxxzero/butterfly>`_ - It is awesome.




