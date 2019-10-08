container_etypes = ('SEDAArchiveTransfer', 'SEDAArchiveUnit')
for otype in container_etypes:
    drop_relation_definition('Activity', 'container', otype)

sql("DELETE FROM container_relation WHERE eid_from IN"
    " (SELECT c.eid_from FROM container_relation AS c"
    "   JOIN entities AS e ON e.eid=c.eid_from WHERE e.type='Activity');")
commit()

sync_schema_props_perms('seda_archive_unit')
sync_schema_props_perms('SEDAArchiveUnit')
