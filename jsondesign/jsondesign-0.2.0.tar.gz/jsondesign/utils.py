"""
Library utils
"""

import json


def explore_paths(schema, root = None):
    """
    Explore a schema and extract its features path recursively
    """

    return_list = list()
    
    properties = schema['allOf'][0]['properties']
    
    required = schema['allOf'][0].get('required') or list()

    for k in properties:
 
        """
        Here type(properties[k]) == dict does not work for referenced schemata. 
        Indeed, the type of a referenced schema is jsonref.JsonRef, 
        even if it is rendered and it acts as a dict.
        Une isinstance instead
        """
        if isinstance(properties[k], dict): # do not explore lists of required properties 
       
            if root:
                key = root+'.'+k
            else:
                key = k

            #else:
            path = {"path" : key, 'type' : properties[k]["type"]}
            if k in required:
                path['required'] = True

            return_list.append(path)

            if properties[k]['type'] == 'object':
                return_list += explore_paths(properties[k],root=key)

    extensions = schema['allOf'][1:]

    for c in extensions:
        data =  explore_paths(c,root=root)
        
        # now we need to check if an item is already in the return_list
        # E.g., you don't want to add {"features": "object"} twice
        for item in data:
            if item not in return_list:
                return_list.append(item)
    
    # TODO: remove possible duplications due to bad modeling
    return return_list
    #return [dict(t) for t in {tuple(d.items()) for d in return_list}]
           




foo = {
    "$id": "las://schema/student",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "allOf": [
        {
            "properties": {
                "features": {
                    "type": "object",
                    "allOf": [
                        {
                            "properties": {
                                "student_id": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "student_id"
                            ]
                        }
                    ]
                }
            }
        },
        {
            "$id": "las://schema/person",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "allOf": [
                    {
                        "properties": {
                            "features": {
                                "type": "object",
                                "allOf": [
                                    {
                                        "properties": {
                                            "firstName": {
                                                "type": "string"
                                            },
                                            "lastName": {
                                                "type": "string"
                                            },
                                            "address": {
                                                "$id": "las://schema/address",
                                                "$schema": "http://json-schema.org/draft-07/schema#",
                                                "type": "object",
                                                "allOf": [
                                                    {
                                                        "properties": {
                                                            "features": {
                                                                "type": "object",
                                                                "allOf": [
                                                                    {
                                                                        "properties": {
                                                                            "street_address": {
                                                                                "type": "string"
                                                                            },
                                                                            "city": {
                                                                                "type": "string"
                                                                            },
                                                                            "state": {
                                                                                "type": "string"
                                                                            }
                                                                        },
                                                                        "required": [
                                                                            "city",
                                                                            "state",
                                                                            "street_address"
                                                                        ]
                                                                    }
                                                                ]
                                                            }
                                                        }
                                                    }
                                                ]
                                            }
                                        },
                                        "required": [
                                            "firstName",
                                            "lastName"
                                        ]
                                    }
                                ]
                            }
                        }
                    }
            ]
        }
    ]
}



def main():
    return explore_paths(foo)

if __name__ == "__main__":
    paths = main()
    print (json.dumps(paths, sort_keys=True, indent=4))
