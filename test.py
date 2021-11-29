from auto_schema.config import get_replicas
from auto_schema.host import Host
from auto_schema.replica_set import ReplicaSet

dc = 'eqiad'
section = 's4'
replica = None

if not replica:
    replicas = get_replicas(dc, section)
else:
    replicas = [replica]
for replica in replicas:
    db = Host(replica, section)
    print(replica, db.get_dbs())

replica_set = ReplicaSet(replicas, section, dc)
replica_set.sql_on_each_db_of_each_replica(
    'desc image;', ticket=None, downtime_hours=None, should_depool=None)
