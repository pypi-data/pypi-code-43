import yaml
import json
document: str = """
    a: 1
    b: {}
    c: []
    d:
     - milk:
       - dairy
       - soy
     - 2
     - 3
     - eggs
"""

data = yaml.load(document)
print(json.dumps(data, indent=2))
print(data)

doc2: str = """
    - apples
    - oranges
    - milk:
        type: dairy
        milkfat: "2%"
"""

print(json.dumps(yaml.load(doc2), indent=2))

doc3: str = """
    - i_text_in_folder: my_special_name
"""
print(json.dumps(yaml.load(doc3), indent=2))

doc4: str = """
- ImmutableBlock:
    - i_outer_nested_keyed_list:
        type: KeyedList
        children:
            - i_inner_nested_keyed_list:
                type: KeyedList
                children:
                    - i_text_in_inner_nested_keyed_list
            - i_text_in_outer_nested_keyed_list
- TemporalBlock:
    - i_outer_nested_keyed_list:
        type: KeyedList
        children:
            - i_inner_nested_keyed_list:
                type: KeyedList
                children:
                    - i_text_in_inner_nested_keyed_list
            - i_text_in_outer_nested_keyed_list
"""
print(json.dumps(yaml.load(doc4), indent=2))

doc5: str = """
- Foo:
    bar:
    baz: 7
    blub: false
    noopies: "bloop"
"""
print(json.dumps(yaml.load(doc5), indent=2))
print(yaml.load(doc5)[0]["Foo"]["noopies"])
