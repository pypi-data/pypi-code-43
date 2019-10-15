from .exception import CastingFailure
import pprint
import logging
import json
logger1 = logging.getLogger(__name__)

class AciSet:
    pass

class AciTree(AciSet):
    pass

class ListOfAciTree(AciSet):
    pass

class AciSet:
    def __init__(self, payload):
        self.__dict__['_total_count'] = None
        self.__dict__['_imdata'] = None
        self.__dict__['_subscription_id'] = None

        if 'totalCount' in payload.keys():
            self.__dict__['_total_count'] = int(payload['totalCount'])

        if 'imdata' in payload.keys():
            self.__dict__['_imdata'] = payload['imdata']

        if 'subscriptionId' in payload.keys():
            self.__dict__['_subscription_id'] = payload['subscriptionId']

    def ltree(self) -> ListOfAciTree:
        return ListOfAciTree({'imdata': self.imdata, 'totalCount': self.total_count})

    def tree(self) -> AciTree:
        if len(self) > 1:
            raise CastingFailure("There is more than 1 tree in the object set")

        return AciTree({'imdata': self.imdata, 'totalCount': self.total_count})

    def search(self, cls = 'unspecified', **kwargs) -> ListOfAciTree:
        '''
        :param aci_class: the name of the class to be found in self._imdata
        :param kwargs: dict of attributes:value
        :return: the list of objects present in self._imdata of class aci_class with attributes matching kwargs. Returns an empty list of no match
        '''
        res = self.__search(self._imdata, '', cls, [], kwargs)
        if len(res) == 0:
            logger1.debug('No object {0} found in the tree'.format(cls))

        #return res
        return ListOfAciTree({'imdata' : res, 'totalCount': len(res)})

    def __search(self, tree, dn, cls, res, kwargs):
        '''
        :param tree: a tree of objects
        :param aci_class: the name of the class to be found in self._imdata
        :param res: a list of object found so far in tree
        :return: the list of objects present in tree of class aci_class with attributes matching kwargs. Returns an empty list of no match
        '''

        if isinstance(tree, list):
            for child in tree:
                self.__search(child, dn, cls, res, kwargs)

        elif isinstance(tree, dict):
            missing_dn = False

            for key in tree.keys():
                if 'attributes' in tree[key].keys() and 'dn' in tree[key]['attributes'].keys():
                    dn = tree[key]['attributes']['dn']

                elif 'attributes' in tree[key].keys() and 'rn' in tree[key]['attributes'].keys():
                    missing_dn = True
                    dn = "{0}/{1}".format(dn, tree[key]['attributes']['rn'])

                if key == cls or cls == 'unspecified':
                    if 'attributes' in tree[key].keys() and self.__match_attribute(tree[key]['attributes'], kwargs):
                        logger1.debug('Object {0} found: {1}'.format(key, tree[key]['attributes']))

                        if missing_dn:
                            tree[key]['attributes']['dn'] = dn

                        res.append(tree)

                elif key != cls:
                    if 'children' in tree[key].keys():
                        self.__search(tree[key]['children'], dn, cls, res, kwargs)

        return res

    def __match_attribute(self, obj, kwargs):
        '''
        :param obj: A dictionary
        :param kwargs: A second dictionary containing the attributes:value to be found in obj
        :return: Return true if all atributes in kwargs are found in obj. False otherwise
        '''

        result = True

        for attr, value in kwargs.items():
            if attr not in obj.keys() or obj[attr] != value:
                result = False

        return result

    @property
    def total_count(self) -> str:
        return self._total_count

    @property
    def imdata(self) -> list:
        return self._imdata

    @property
    def subscription_id(self) -> str:
        return self._subscription_id

    def __len__(self):
        return self.total_count


class ListOfAciTree(AciSet):
    def __init__(self, response):
        super().__init__(response)

    def __iter__(self) -> AciTree:
        for el in self.imdata:
            yield AciTree({'imdata' : [el]})

    def __getitem__(self, item) -> AciTree:
        return AciTree({'imdata': [self.imdata[item]], 'totalCount': 1})

    def __repr__(self):
        return json.dumps(self.imdata)

    def __str__(self):
        return json.dumps(self.imdata)


class AciTree(AciSet):
    def __init__(self, response):
        super().__init__(response)

    def __getattr__(self, attr):
        cls = list(self.imdata[0].keys())[0]
        return self.imdata[0][cls]['attributes'][attr]

    def __setattr__(self, key, value):
        cls = list(self.imdata[0].keys())[0]
        self.imdata[0][cls]['attributes'][key] = value

    def __repr__(self):
        return json.dumps(self.imdata[0])

    def __str__(self):
        return json.dumps(self.imdata[0])

    def update_cls(self, new_cls):
        old_cls = list(self.imdata[0].keys())[0]
        self.imdata[0] = {new_cls: self.imdata[0][old_cls]}

    def cls(self) -> str:
        return list(self.imdata[0].keys())[0]

    def children(self) -> ListOfAciTree:
        if self.total_count > 0:
            cls = list(self.imdata[0].keys())[0]

            if "children" in self.imdata[0][cls].keys():
                return ListOfAciTree({'imdata' : self.imdata[0][cls]['children'], 'tocal_count': len(self.imdata[0][cls]['children'])})

        else:
            return ListOfAciTree({'imdata': [], 'total_count': 0})


def to_tree(ltree: ListOfAciTree) -> AciTree:
    return AciSet.tree(ltree)

def to_ltree(tree: AciTree) -> ListOfAciTree:
    return AciSet.ltree(tree)

def mpprint(obj: AciSet):
    pprint.pprint(obj.imdata[0])

