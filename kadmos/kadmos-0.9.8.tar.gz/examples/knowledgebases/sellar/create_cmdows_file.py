from kadmos.cmdows import CMDOWS

cmdows = CMDOWS()

dcs = ['A', 'B', 'C', 'D1', 'D2', 'E', 'F', 'G1', 'G2', 'H']


cmdows.add_header('Imco van Gent', 'CMDOWS file for the Sellar database.', '2018-05-23T11:19:56.287006',
                  fileVersion='1.0')

cmdows.add_contact('Imco van Gent', 'i.vangent@tudelft.nl', 'imcovangent',
                   company='TU Delft',
                   department='Flight Performance and Propulsion',
                   function='PhD Student',
                   address='Kluyverweg 1, 2629 HS, Delft',
                   country='The Netherlands',
                   telephone='0031 6 53 89 42 75',
                   roles=['architect', 'integrator'])

for dc in dcs:
    if not '1' in dc and not '2' in dc:
        uid = dc
        id = dc
        mode = 'main'
        label = dc
    else:
        if '1' in dc:
            keyword = '1'
        else:
            keyword = '2'
        id = dc.replace(keyword, '')
        uid = id + '[' + keyword + ']'
        mode = keyword
        label = uid

    cmdows.add_dc(uid, id, mode, instance_id=1, version='1.0', label=label)

    cmdows.add_dc_general_info(uid,
                               description='{} discipline of the Sellar tool set.'.format(dc),
                               status='Available',
                               owner_uid='imcovangent',
                               creator_uid='imcovangent',
                               operator_uid='imcovangent')
    cmdows.add_dc_licensing(uid,
                            license_type='open-source',
                            license_specification='Apache License 2.0',
                            license_info='https://www.apache.org/licenses/LICENSE-2.0')

cmdows.save('database_overview.xml', pretty_print=True)