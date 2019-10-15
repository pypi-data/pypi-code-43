import json


def load_terraform_outputs_file(file_path):
    """load_terraform_outputs_file Import JSON file of terraform outputs

    Arguments:
        file_path {str} -- File to be loaded

    Returns:
        [dict] -- {variable_name: variable_value}
    """
    try:
        state = json.loads(open(file_path).read().strip())
        return {k: data["value"] for k, data in state.items()}
    except json.decoder.JSONDecodeError:
        return {}
