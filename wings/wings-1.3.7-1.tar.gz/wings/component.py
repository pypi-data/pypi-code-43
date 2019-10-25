import json
import os
import re


class Component(object):
    def __init__(self, api_client):
        self.api_client = api_client

    def get_type_id(self, typeid):
        if typeid == "":
            return self.api_client.topcls
        elif not re.match(r"(http:|https:)//", typeid):
            return self.api_client.libns + typeid + "Class"
        else:
            return typeid + "Class"

    def get_component_id(self, compid):
        if compid is None:
            return ""
        elif not re.match(r"(http:|https:)//", compid):
            return self.api_client.libns + compid
        else:
            return compid

    def new_component_type(self, ctype, parent):
        ptype = self.get_component_id(parent)
        ctype = self.get_component_id(ctype)
        pcls = self.get_type_id(ptype)
        postdata = {'parent_cid': ptype, 'parent_type': pcls,
                    'cid': ctype, 'load_concrete': "false"}
        resp = self.api_client.session.post(self.api_client.get_request_url() +
                                            'components/type/addComponent', postdata)
        self.api_client.check_request(resp)

    def new_component(self, cid, parent):
        pid = self.get_component_id(parent)
        cid = self.get_component_id(cid)
        pcls = self.get_type_id(pid)
        postdata = {'parent_cid': pid, 'parent_type': pcls,
                    'cid': cid, 'load_concrete': "true"}
        resp = self.api_client.session.post(self.api_client.get_request_url() +
                                            'components/addComponent', postdata)
        self.api_client.check_request(resp)

    def del_component_type(self, ctype):
        ctype = self.get_component_id(ctype)
        postdata = {'cid': ctype}
        resp = self.api_client.session.post(self.api_client.get_request_url() +
                                            'components/type/delComponent', postdata)
        self.api_client.check_request(resp)

    def del_component(self, cid):
        cid = self.get_component_id(cid)
        postdata = {'cid': cid}
        resp = self.api_client.session.post(self.api_client.get_request_url() +
                                            'components/delComponent', postdata)
        self.api_client.check_request(resp)

    def get_all_items(self):
        resp = self.api_client.session.get(
            self.api_client.get_request_url() + 'components/getComponentHierarchyJSON')
        self.api_client.check_request(resp)
        return resp.json()

    def get_component_description(self, cid):
        cid = self.get_component_id(cid)
        postdata = {'cid': cid}
        resp = self.api_client.session.get(
            self.api_client.get_request_url() + 'components/getComponentJSON', params=postdata)
        self.api_client.check_request(resp)
        return resp.json()

    def get_component_type_description(self, ctype):
        ctype = self.get_type_id(ctype)
        postdata = {'cid': ctype, 'load_concrete': False}
        resp = self.api_client.session.get(
            self.api_client.get_request_url() + 'components/type/getComponentJSON', params=postdata)
        self.api_client.check_request(resp)
        return resp.json()

    def _modify_component_json(self, cid, jsonobj):
        for input in jsonobj["inputs"]:
            input["type"] = input["type"].replace("xsd:", self.api_client.xsdns)
            input["type"] = input["type"].replace("dcdom:", self.api_client.dcdom)
            input["id"] = cid + "_" + input["role"]
        for output in jsonobj["outputs"]:
            output["type"] = output["type"].replace("xsd:", self.api_client.xsdns)
            output["type"] = output["type"].replace("dcdom:", self.api_client.dcdom)
            output["id"] = cid + "_" + output["role"]
        jsonobj["id"] = cid
        return jsonobj

    def save_component(self, cid, jsonobj):
        cid = self.get_component_id(cid)
        jsonobj = self._modify_component_json(cid, jsonobj)
        jsonobj["type"] = 2
        postdata = {'component_json': json.dumps(jsonobj), 'cid': cid}
        resp = self.api_client.session.post(self.api_client.get_request_url() +
                                            'components/saveComponentJSON', postdata)
        self.api_client.check_request(resp)

    def save_component_type(self, ctype, jsonobj):
        ctype = self.get_type_id(ctype)
        jsonobj = self._modify_component_json(ctype, jsonobj)
        jsonobj["type"] = 1
        postdata = {'component_json': json.dumps(jsonobj), 'cid': ctype,
                    'load_concrete': False}
        self.api_client.session.post(self.api_client.get_request_url() +
                                     'components/type/saveComponentJSON', postdata)

    def download_component(self, cid, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_path = "{}.zip".format(os.path.join(dir_path, cid))
        cid = self.get_component_id(cid)
        params = {'cid': cid}
        r = self.api_client.session.get(self.api_client.get_request_url() +
                            'components/fetch', params=params)
        with open(file_path, 'wb') as f:
            f.write(r.content)
        return file_path

    def upload_component(self, filepath, cid):
        cid = self.get_component_id(cid)
        fname = os.path.basename(filepath)
        files = {"file": (fname, open(filepath, "rb"))}
        postdata = {"name": fname, "type": "component", "id": cid}
        response = self.api_client.session.post(
            self.api_client.get_request_url() + "upload", data=postdata, files=files
        )
        if response.status_code == 200:
            details = response.json()
            if details["success"]:
                loc = os.path.basename(details["location"])
                self.set_component_location(cid, details["location"])
                return loc

    def set_component_location(self, cid, location):
        postdata = {'cid': self.get_component_id(cid), 'location': location}
        self.api_client.session.post(self.api_client.get_request_url() +
                                     'components/setComponentLocation', postdata)

    def upload(self, filepath, cid):
        cid = self.get_component_id(cid)
        fname = os.path.basename(filepath)
        files = {'file': (fname, open(filepath, 'rb'))}
        postdata = {'id': cid, 'name': fname, 'type': 'component'}
        response = self.api_client.session.post(self.api_client.get_request_url() + 'upload',
                                                data=postdata, files=files)
        if response.status_code == 200:
            details = response.json()
            print(details)
            if details['success']:
                componentid = os.path.basename(details['location'])
                componentid = re.sub(r"(^\d.+$)", r"_\1", componentid)
                print(componentid)
                self.set_component_location(componentid, details['location'])
                return componentid
