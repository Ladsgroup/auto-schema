from auto_schema.config import get_replicas
from auto_schema.host import Host

dc = 'eqiad'
section = 's4'
replica = 'db1142'

if not replica:
    replicas = get_replicas(dc, section)
else:
    replicas = [replica]
for replica in replicas:
    # TODO: Make sure it handles replicass with replicas (sanitarium master,
    # cloud, etc.) properly
    db = Host(replica, section)
    print(replica, db.has_replicas())
