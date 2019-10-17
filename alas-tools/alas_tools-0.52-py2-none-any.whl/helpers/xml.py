

def get_first_xml_child_node(node, child_tag):
    nodes = filter(lambda x: x.tag == child_tag, node.getchildren())
    return nodes[0] if len(nodes) > 0 else None
