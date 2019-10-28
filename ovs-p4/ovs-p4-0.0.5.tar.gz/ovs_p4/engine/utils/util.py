

def make_entries_data(match_keys=None, action_name=None, action_params=None):
    entry_obj = dict(match_keys=match_keys,
                     action_name=action_name,
                     action_params=action_params)

    return entry_obj