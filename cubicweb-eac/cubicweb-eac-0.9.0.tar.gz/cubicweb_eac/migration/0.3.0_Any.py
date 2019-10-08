eac_version = cnx.vreg.config.cube_version('eac')

# Needed to fix an error on migrations because of some evolution in the 0.9.0 schema
# brought by reusing the names `start_date` `end_date` 
if eac_version > (0, 3, 0) and eac_version <= (0, 9, 0):
    add_attribute('ChronologicalRelation', 'start_date', commit=False)
    add_attribute('ChronologicalRelation', 'end_date')

for etype in ('AssociationRelation', 'ChronologicalRelation', 'HierarchicalRelation'):
    add_attribute(etype, 'entry')

add_entity_type('NameEntry')
with cnx.deny_all_hooks_but('metadata'):
    for record in rql('Any X,XN WHERE X is AuthorityRecord, X name XN',
                      ask_confirm=False).entities():
        create_entity('NameEntry', parts=record.name, form_variant=u'authorized',
                      name_entry_for=record, ask_confirm=False)
commit(ask_confirm=False)
drop_attribute('AuthorityRecord', 'name')

add_attribute('Activity', 'agent')

sync_schema_props_perms('has_citation', syncperms=False)
