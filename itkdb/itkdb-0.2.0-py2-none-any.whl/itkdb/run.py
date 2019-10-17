import itkdb

client = itkdb.Client()
comps = client.get(
    'listComponents', json={'project': 'P', 'pageInfo': {'pageSize': 32}}
)

for i, comp in enumerate(comps):
    print(i, comp['code'])
