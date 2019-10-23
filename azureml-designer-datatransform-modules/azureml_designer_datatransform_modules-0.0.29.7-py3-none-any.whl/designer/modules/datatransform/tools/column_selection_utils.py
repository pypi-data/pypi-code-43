from azureml.studio.core.utils.column_selection import ColumnSelection, ColumnSelectionRuleSet, ColumnSelectionRule
import json

# def convert_column_selection_rule_set_to_json_obj(rule_set:ColumnSelectionRuleSet):
#     rules_dict = {
#         ColumnSelectionRuleSet.IS_FILTER: rule_set.is_filter,
#         ColumnSelectionRuleSet.RULES: [conver_column_selection_rule_to_json_obj(r) for r in rule_set.rules]
#         }
#     return rules_dict

# def conver_column_selection_rule_to_json_obj(rule:ColumnSelectionRule):
#     return {
#             ColumnSelectionRule.RULE_TYPE: rule.rule_type,
#             ColumnSelectionRule.IS_EXCLUDE: rule.is_exclude,
#             ColumnSelectionRule.COLUMNS: rule.columns,
#             ColumnSelectionRule.COLUMN_TYPES: rule.column_types
#             }

def convert_column_selection_to_json(column_selection:ColumnSelection):
    return json.dumps(column_selection._obj)