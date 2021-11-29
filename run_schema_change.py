from auto_schema.replica_set import ReplicaSet

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
# Use None instead of [] to get all pooled replicas
# Note: It ignores any replicas that have replicas
replicas = ['dbstore1007:3314']


replica_set = ReplicaSet(replicas, section, dc)
replica_set.sql_on_each_replica(command, ticket=ticket, downtime_hours=downtime_hours, should_depool=should_depool)
