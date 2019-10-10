from importFromParent import importFromParent


def test(string: str, start = 'TEST:', space_after_start: bool = True, not_string: dict = {'before':'', 'after':'', 'both':'"'}, end='.'):
    space = notMS1 = notMS2 = ''
    if space_after_start:
        space = ' '
    if not_string['before'] != not_string['after']:
        if not_string['both'] == '':
            raise Exception('''if "before" and "after" are different, "both" can not be <@void/@nothing/""/''>!''')
        else:
            notMS1 = notMS2 = not_string['both']
    else:
        if not_string['both'] != '':
            if not_string['after'] == '':
                notMS1 = notMS2 = not_string['both']
            else:
                raise Exception('''if "before" and "after" are equal and different of <@void/@nothing/""/''>!, "both" can only be <@void/@nothing/""/''>!''')
        else:
            notMS1 = notMS2 = not_string['after']
    print(f'{start}{space}{notMS1}{string}{notMS2}{end}')
