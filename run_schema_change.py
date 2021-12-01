from auto_schema.schema_change import SchemaChange

section = 's4'
should_depool = True
downtime_hours = 4
should_downtime = True
ticket = 'T277354'

# Don't add set session sql_log_bin=0;
command = """ALTER TABLE filearchive  CHANGE  fa_major_mime fa_major_mime ENUM('unknown','application','audio','image','text','video','message','model','multipart','chemical') default 'unknown';
ALTER TABLE image  CHANGE  img_major_mime img_major_mime ENUM('unknown','application','audio','image','text','video','message','model','multipart','chemical') default 'unknown';
ALTER TABLE oldimage CHANGE  oi_major_mime oi_major_mime ENUM('unknown','application','audio','image','text','video','message','model','multipart','chemical') default 'unknown';"""

# Set this to false if you don't want to run on all dbs
# In that case, you have to specify the db in the command.
all_dbs = True

# DO NOT FORGET to set the right port if it's not 3306
# Use None instead of [] to get all pooled replicas
# Note: It ignores any replicas that have replicas
replicas = ['db2117', 'db2124', 'db2141:3316']

# Should return true if schema change is applied


def check(db):
    return 'chemical' in db.run_sql('desc image;')


schema_change = SchemaChange(
    replicas=replicas,
    section=section,
    all_dbs=all_dbs,
    check=check,
    command=command,
    ticket=ticket,
    downtime_hours=downtime_hours,
    should_depool=should_depool
)
schema_change.run()
