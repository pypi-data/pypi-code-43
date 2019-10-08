from .records import list_records

def get_diff(conf, comparison_treeish, base_treeish):
    comparison_record_ids = set(list_records(conf, comparison_treeish))
    base_record_ids = set(list_records(conf, base_treeish))
    added_records = comparison_record_ids - base_record_ids
    removed_records = base_record_ids - comparison_record_ids
    return list(added_records), list(removed_records)
