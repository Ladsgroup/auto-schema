import sys

from auto_schema.config import get_replicas
from auto_schema.db_actions import Db

dc = 'eqiad'
section = 's8'
downtime_hours = 4
ticket = 'T296274'
replicas = ['db1177']
pooled_replicas = get_replicas(dc, section)

if not replicas:
    replicas = pooled_replicas


for replica in replicas:
    # TODO: Make sure it handles replicass with replicas (sanitarium master)
    # properly
    db = Db(replica, section)
    should_depool = True

    # don't depool replicas that are not pooled in the first place (dbstore, backup source, etc.)
    if replica not in pooled_replicas:
        should_depool = False

    db.downtime(ticket, str(downtime_hours))
    if should_depool:
        db.depool(ticket)