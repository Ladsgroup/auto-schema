import sys

from config import get_replicas
from db_actions import Db

dc = 'eqiad'
section = 's5'
downtime_hours = 4
ticket = 'T249683'
# Don't add set session sql_log_bin=0;
# TODO: Make it discover databases.
command = 'REVOKE DROP ON \\`%wik%\\`.* FROM wikiadmin@\'10.%\';'
# DO NOT FORGET to set the right port if it's not 3306
replicas = None
pooled_replicas = get_replicas(dc, section)

if not replicas:
    replicas = pooled_replicas


for replica in replicas:
    # TODO: Make sure it handles replicass with replicas (sanitarium master)
    # properly
    db = Db(replica, section)
    res = db.run_sql('set session sql_log_bin=0; ' + command)
    if 'error' in res.lower():
        print('PANIC: Schema change errored. Not repooling')
        sys.exit()
