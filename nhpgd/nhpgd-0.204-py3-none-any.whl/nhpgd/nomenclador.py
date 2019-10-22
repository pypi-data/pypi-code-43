"""
Nomenclador para hospitales públicos de gestión descentralizada de Argentina
"""
import csv
import requests
import os
import json


class Nomenclador:

    url_csv = 'https://docs.google.com/spreadsheets/d/15r_GRQPtYWRFcAbLNHO2yktCXj5V2-xmkkTC7eGh8TM/export?format=csv&gid=0'
    here = os.path.dirname(os.path.realpath(__file__))
    data_folder = os.path.join(here, 'data')
    local_csv = os.path.join(data_folder, 'nomenclador.csv')
    local_json = os.path.join(data_folder, 'nomenclador.json')

    def __init__(self):
        if not os.path.isfile(self.local_csv):
            self.download_csv()
        self.read_csv()
    
    def download_csv(self):
        req = requests.get(self.url_csv)
        if not os.path.isdir(self.data_folder):
            os.mkdir(self.data_folder)
        f = open(self.local_csv, 'wb')
        f.write(req.content)
        f.close()

    def read_json(self):
        # read defined JSON an load to the _self.tree_ property
        if os.path.isfile(self.local_json):
            f = open(self.local_json, 'r')
            self.tree = json.load(f)
            f.close
        else:
            self.read_csv()

    def read_csv(self):
        # read CSV and transfor to a useful JSON
            
        tree = {}   # results
        fieldnames = ['codigo', 'descripcion', 'arancel', 'observaciones']
        f = open(self.local_csv, 'r')
        reader = csv.DictReader(f, fieldnames=fieldnames)
        next(f)  # headers
        errors = []
        c = 0  # codigo unico (no hay otro)
        
        for row in reader:
            # fix all shit
            for k, v in row.items():
                row[k] = v.strip()

            if row['codigo'] is None or row['codigo'] == '':
                row['codigo'] = tree[c-1]['codigo']
            
            # para saber si copio el arancel este tiene que ser el mismo código que el anterior
            if c > 0 and row['codigo'] == tree[c-1]['codigo']:  # este codigo esta dentro del anterior
                if row['arancel'] is None or row['arancel'] == '':
                    row['arancel'] = tree[c-1]['arancel']
            
            tree[c] = row
            c += 1

        f.close()

        f2 = open(self.local_json, 'w')
        f2.write(json.dumps(tree, indent=2))
        f2.close

        self.tree = tree
    
    def search(self, codigo=None, txt=None):
        # buscar por código (identico) o por texto (en todos los campos, incluso codigo)
        for code, content in self.tree.items():
            if code is not None:
                if content['codigo'] == codigo:
                    yield content
            if txt is not None:
                # saca del medio, Solr
                full_str = ' '.join([str(val).lower() for key, val in content.items()])
                if full_str.find(txt.lower()) > -1:
                    yield content
    
    def code_exists(self, codigo):
        exist = False
        for nom in self.search(codigo=codigo):
            exist = True
            break
        return exist

    def save_csv(self, path):
        f = open(path, 'w')
        fieldnames = ['codigo', 'descripcion', 'arancel', 'observaciones']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for i, nom in n.tree.items():
            writer.writerow(nom)
        f.close
