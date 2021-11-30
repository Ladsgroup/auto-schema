import sys

import requests

from .config import get_replicas
from .db import Db
from .host import Host


class ReplicaSet(object):
    def __init__(self, replicas, section, dc):
        if replicas is None:
            replicas = get_replicas(dc, section)
        self.replicas = replicas
        self.section = section
        self.pooled_replicas = get_replicas(dc, section)
        self.dbs = []

    def sql_on_each_replica(self, sql, ticket=None,
                            should_depool=True, downtime_hours=4, check=None):
        for host in self._per_replica_gen(
                ticket, should_depool, downtime_hours):
            if check:
                if check(host):
                    print('Already applied, skipping')
                    continue
            res = host.run_sql('set session sql_log_bin=0; ' + sql)
            if 'error' in res.lower():
                print('PANIC: Schema change errored. Not repooling and stopping')
                sys.exit()
            if check and not check(host):
                print('PANIC: Schema change was not applied. Not repooling and stopping')
                sys.exit()

    def sql_on_each_db_of_each_replica(
            self, sql, ticket=None, should_depool=True, downtime_hours=4, check=None):
        for host in self._per_replica_gen(
                ticket, should_depool, downtime_hours):
            res = self.run_sql_per_db(
                host, 'set session sql_log_bin=0; ' + sql, check)
            if 'error' in res.lower():
                print('PANIC: Schema change errored. Not repooling')
                sys.exit()

    def _per_replica_gen(self, ticket, should_depool, downtime_hours):
        for replica in self.replicas:
            # TODO: Make sure it handles replicass with replicas (sanitarium master)
            # properly
            host = Host(replica, self.section)
            if host.has_replicas():
                print('Ignoring {} as it has hanging replicas'.format(replica))
                if '--run' in sys.argv:
                    continue
            should_depool_this_host = should_depool

            # don't depool replicas that are not pooled in the first place
            # (dbstore, backup source, etc.)
            if replica not in self.pooled_replicas:
                should_depool_this_host = False

            if downtime_hours:
                host.downtime(ticket, str(downtime_hours))
            if should_depool_this_host:
                host.depool(ticket)

            yield host
            if should_depool_this_host:
                host.repool(ticket)

    def get_dbs(self):
        if not self.dbs:
            if self.section.startswith('s'):
                url = 'https://noc.wikimedia.org/conf/dblists/{}.dblist'.format(
                    self.section)
                wikis = [i.strip() for i in requests.get(url).text.split(
                    '\n') if not i.startswith('#') and i.strip()]
                self.dbs = wikis
            else:
                # TODO: Build a way to get dbs of es and pc, etc.
                pass

        return self.dbs

    def run_sql_per_db(self, host, sql, check):
        res = ''
        for db_name in self.get_dbs():
            db = Db(host, db_name)
            if check:
                if check(db):
                    print('Already applied, skipping')
                    continue
            res += db.run_sql(sql)
            if check:
                if not check(db):
                    print('Schema change was not applied, panicking')
                    res += 'Error: Schema change was not applied, panicking'
        return res
