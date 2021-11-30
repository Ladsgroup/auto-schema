from auto_schema.schema_change import SchemaChange

dc = 'eqiad'
section = 's4'
should_depool = True
downtime_hours = 4
should_downtime = True
ticket = 'T296143'

# Don't add set session sql_log_bin=0;
command = 'OPTIMIZE TABLE commonswiki.image;'

# Set this to false if you don't want to run on all dbs
# In that case, you have to specify the db in the command.
all_dbs = True

# DO NOT FORGET to set the right port if it's not 3306
# Use None instead of [] to get all pooled replicas
# Note: It ignores any replicas that have replicas
replicas = ['dbstore1007:3314']

# Should return true if schema change is applied
def check(db):
    return 'chemical' in db.run_sql('desc image;')


schema_change = SchemaChange(
    replicas=replicas,
    section=section,
    dc=dc,
    all_dbs=all_dbs,
    check=check,
    command=command,
    ticket=ticket,
    downtime_hours=downtime_hours,
    should_depool=should_depool
)
schema_change.run()
