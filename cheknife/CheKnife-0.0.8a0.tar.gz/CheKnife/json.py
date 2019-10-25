import json

def fix_json(json_message=None):
    try:
        result = json.loads(json_message)
    except Exception as e:
        # Find the offending character index:
        idx_to_replace = int(str(e).split(' ')[-1].replace(')', ''))

        # Remove the offending character:
        json_message = list(json_message)
        try:
            json_message[idx_to_replace] = ' '
        except IndexError:
            logger.error('Coud not decode json from: {}'.format(''.join(json_message)))
            return {}

        new_message = ''.join(json_message)
        return fix_json(json_message=new_message)
    return result
