import sys

from auto_schema.config import get_replicas
from auto_schema.host import Host

dc = 'eqiad'
section = 's8'
downtime_hours = 4
ticket = 'T296274'
replicas = ['db1177']
pooled_replicas = get_replicas(dc, section)

if not replicas:
    replicas = pooled_replicas


for replica in replicas:
    db = Host(replica, section)
    should_depool = True

    if replica not in pooled_replicas:
        should_depool = False

    db.downtime(ticket, str(downtime_hours))
    if should_depool:
        db.depool(ticket)
