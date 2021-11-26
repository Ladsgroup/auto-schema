from config import get_replicas
from db_actions import Db

dc = 'eqiad'
section = 's4'
shouldDepool = True
downtimeHours = 4
shouldDowntime = True
ticket = 'T296143'
# Don't add set session sql_log_bin=0;
command = 'OPTIMIZE TABLE commonswiki.image;'
replica = 'db1142'

if not replica:
    replicas = get_replicas(dc, section)
else:
    replicas = [replica]
for replica in replicas:
    # TODO: Make sure it handles replicass with replicas (sanitarium master,
    # cloud, etc.) properly
    db = Db(replica, section)
    print(db.has_traffic())
