import sys

from config import get_replicas
from db_actions import Db

dc = 'eqiad'
section = 's4'
should_depool = True
downtime_hours = 4
should_downtime = True
ticket = 'T296143'
# Don't add set session sql_log_bin=0;
# TODO: Make it discover databases.
command = 'OPTIMIZE TABLE commonswiki.image;'
# DO NOT FORGET to set the right port if it's not 3306
replicas = ['dbstore1007:3314']
pooled_replicas = get_replicas(dc, section)

if not replicas:
    replicas = pooled_replicas


for replica in replicas:
    # TODO: Make sure it handles replicass with replicas (sanitarium master)
    # properly
    db = Db(replica, section)
    should_depool_this_db = should_depool

    # don't depool replicas that are not pooled in the first place (dbstore, backup source, etc.)
    if replica not in pooled_replicas:
        should_depool_this_db = False

    if should_downtime:
        db.downtime(ticket, str(downtime_hours))
    if should_depool_this_db:
        db.depool(ticket)
    res = db.run_sql('set session sql_log_bin=0; ' + command)
    if 'error' in res.lower():
        print('PANIC: Schema change errored. Not repooling')
        sys.exit()
    if should_depool_this_db:
        db.repool(ticket)
