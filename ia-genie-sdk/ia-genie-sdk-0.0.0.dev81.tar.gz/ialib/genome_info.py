try:
    from cyjupyter import Cytoscape
except:
    class Cytoscape:
        def __init__(*args, **kwargs):
            pass


class Genome:
    def __init__(self, topology):
        self.topology = topology
        self.agent = self.topology['agent']
        self.description = self.topology['description']
        self.style_obj = self.topology['style']
        self.style_obj[1]['style']['curve-style'] = 'bezier'
        #        self.agent_genome = self.topology['elements']['nodes']
        self.primitives = {}
        self.manipulatives = {}
        self.action_ids = []
        self.actions_manifests = {}
        for node in self.topology['elements']['nodes']:
            if node['data']['type'] == 'primitive':
                self.primitives[node['data']['id']] = node['data']
            elif node['data']['type'] == 'manipulative':
                self.manipulatives[node['data']['id']] = node['data']
                if node['data']['name'].startswith("ACTION"):
                    self.action_ids.append(node['data']['id'])
                    if node['data']['primitive'] in self.actions_manifests:
                        self.actions_manifests[node['data']['primitive']].append(node['data'])
                    else:
                        self.actions_manifests[node['data']['primitive']] = [node['data']]
        self.agent_genome = {'primitives': self.primitives, 'manipulatives': self.manipulatives}
        self.primitive_map = {x['name']: _id for _id, x in self.primitives.items()}
        self.manipulative_map = {_id: x['name'] for _id, x in self.manipulatives.items()}
        print(" %s total primitives" % (len(self.primitives)))
        print(" %s total manipulatives" % (len(self.manipulatives)))
        print(" %s total actions" % (len(self.actions_manifests)))
        return

    def get_nodes(self):
        return self.agent_genome['primitives'], self.agent_genome['manipulatives']

    def get_actions(self):
        return self.action_ids

    def get_primitive_map(self):
        return self.primitive_map

    def get_manipulative_map(self):
        return self.manipulative_map

    def change_genes(self, gene_data):
        ## TODO: find id, gene, and replace value.
        return

    def display(self):
        return Cytoscape(data=self.topology, visual_style=self.style_obj, layout={'height': '500px'},
                         background='white')
