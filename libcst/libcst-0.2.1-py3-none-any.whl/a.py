# we want to replace the old_value as new_value
node = cst.parse_statement("fn(a = "old_value", b = 2)")
updated_node = node.deep_replace(node.args[0].value, node.args[0].value.with_changes(value="new_value"))
# note: we cannot pass node.args[0].value.value to deep_replace since it's a str instead of a CSTNode.
