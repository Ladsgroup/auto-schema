from config import get_replicas
import sys

from host import Host


class ReplicaSet(object):
    def __init__(self, replicas, section, dc):
        if replicas is None:
            replicas = get_replicas(dc, section)
        self.replicas = replicas
        self.section = section
        self.pooled_replicas = get_replicas(dc, section)
    
    def sql_on_each_replica(self, sql, ticket=None, should_depool=True, downtime_hours=4):
        for replica in self.replicas:
            # TODO: Make sure it handles replicass with replicas (sanitarium master)
            # properly
            host = Host(replica, self.section)
            if host.has_replicas():
                print('Ignoring {} as it has hanging replicas'.format(replica))
                if '--run' in sys.argv:
                    continue
            should_depool_this_host = should_depool

            # don't depool replicas that are not pooled in the first place (dbstore, backup source, etc.)
            if replica not in self.pooled_replicas:
                should_depool_this_host = False

            if downtime_hours:
                host.downtime(ticket, str(downtime_hours))
            if should_depool_this_host:
                host.depool(ticket)
            res = host.run_sql('set session sql_log_bin=0; ' + sql)
            if 'error' in res.lower():
                print('PANIC: Schema change errored. Not repooling')
                sys.exit()
            if should_depool_this_host:
                host.repool(ticket)