import os

jmx = ''' -Dcom.sun.management.jmxremote=true -Dcom.sun.management.jmxremote.port=6001 -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false '''
agent = ' -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=0.0.0.0:5001 '
param = ' -Xms8g -Xmx8g -XX:MaxGCPauseMillis=100 -Xlog:gc*:log_%t.log:time,level '
os.system('java' + jmx + agent + param + '-jar littlebug-0.1.0.jar')