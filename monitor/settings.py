#!/usr/bin/python
# -*- coding: utf-8 -*-

#!/usr/bin/python
# -*- coding: utf-8 -*-

#URL that will be checked
pageUrl = 'http://abc.com'
#delay
loopSleep = 120
startCmd = '/home/share/sh/tomcat6_start.sh'
killPsWith = '/home/share/tomcat6/bin/bootstrap.jar'
#patch for log files that will be copied (only last lines) in case of a problem with pageUrl page.
logFiles = ('/home/share/tomcat6/logs/catalina.out', '/data/webapps/app/WEB-INF/logs/log.log')
logFilePatterns = ('/data/webapps/app/WEB-INF/logs/*.log',)  # needs to have "," at the end!

