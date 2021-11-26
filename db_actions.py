import sys
import time
import re

from bash import run


class Db(object):
    def __init__(self, replica, section):
        self.replica = replica
        self.section = section
        if re.findall(r'\w1\d{3}', replica):
            self.dc = 'eqiad'
        else:
            self.dc = 'codfw'
        self.fqn = '{}.{}.wmnet'.format(replica.split(':')[0], self.dc)

    def run_sql(self, sql):
        args = '-h{} -P{}'.format(self.replica.split(':')[0], self.replica.split(':')[
                                  1]) if ':' in self.replica else '-h' + self.replica
        if '"' in sql:
            sql = sql.replace('"', '\\"')
        if not sql.strip().endswith(';'):
            sql += ';'
        return run('mysql.py {} -e "{}"'.format(args, sql))

    def run_on_host(self, command):
        if '"' in command:
            command = command.replace('"', '\\"')
        return run('cumin {} "{}"'.format(self.fqn, command))

    def depool(self, ticket):
        # TODO: check if it's depoolable
        run('dbctl instance {} depool'.format(self.replica))
        run('dbctl config commit -b -m "Depooling {} ({})"'.format(self.replica, ticket))
        while True:
            if self.has_traffic() and '--run' in sys.argv:
                print('Sleeping for the traffic to drain')
                time.sleep(60)
            else:
                break

    def has_traffic(self):
        # TODO: Make the users check more strict and include root
        result = self.run_sql(
            'SELECT * FROM information_schema.processlist WHERE User like \'%wiki%\';')
        return bool(result)

    def get_replag(self):
        query_res = self.run_sql(
            "SELECT greatest(0, TIMESTAMPDIFF(MICROSECOND, max(ts), UTC_TIMESTAMP(6)) - 500000)/1000000 AS lag FROM heartbeat.heartbeat WHERE datacenter='{}' GROUP BY shard HAVING shard = '{}';".format(
                self.dc,
                self.section))
        replag = None
        if not query_res:
            return 1000 if '--run' in sys.argv else 0
        for line in query_res.split('\n'):
            if not line.strip():
                continue
            count = line.strip()
            if count == 'lag':
                continue
            try:
                count = float(count)
            except BaseException:
                continue
            replag = count
        return replag

    def repool(self, ticket):
        replag = 1000
        while replag > 1:
            replag = self.get_replag()
            if ((replag is None) or (replag > 1)) and '--run' in sys.argv:
                print('Waiting for replag to catch up')
                time.sleep(60)

        for percent in [10, 25, 75, 100]:
            run('dbctl instance {} pool -p {}'.format(self.replica, percent))
            run('dbctl config commit -b -m "After maintenance {} ({})"'.format(self.replica, ticket))
            if '--run' in sys.argv and percent != 100:
                print('Waiting for the next round')
                time.sleep(900)

    def downtime(self, ticket, hours):
        run('cookbook sre.hosts.downtime --hours {} -r "Maintenance {}" {}'.format(hours, ticket, self.fqn))
