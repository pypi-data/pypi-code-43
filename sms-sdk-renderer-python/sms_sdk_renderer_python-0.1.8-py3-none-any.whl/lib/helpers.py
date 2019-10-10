import pybars

def _header(this, options, items):
    result = [u'<tr>']
    if items['select']['position'] == 'left':
        if items['select']['type'] == 'button':
            result.append(u'<td>Select</td>')
        else:
            result.append(u'<td><input type="checkbox" name="tablesel-header" /></td>')
        for item in items['header_list']:
            result.append(u'<td>')
            result.append(item)
            result.append(u'</td>')
    else:
        if items['select']['type'] == 'button':
            for item in items['header_list']:
                result.append(u'<td>')
                result.append(item)
                result.append(u'</td>')
            result.append(u'<td>Select</td>')
        else:
            for item in items['header_list']:
                result.append(u'<td>')
                result.append(item)
                result.append(u'</td>')
            result.append(u'<td><input type="checkbox" name="tablesel-header" /></td>')
    result.append(u'</tr>')
    return result

def _body(this, options, items):
    result = []
    if items['select']['position'] == 'left':
        for row in items['body']:
            result.append(u'<tr>')
            if items['select']['type'] == 'button':
                result.append(u'<td><button type="action" name="tablesel-row-button">SELECT</button></td>')
            else:
                result.append(u'<td><input type="checkbox" name="tablesel-header" /></td>')
            for item in row:
                result.append(u'<td>')
                result.append(item)
                result.append(u'</td>')
            result.append(u'</tr>')
    else:
        for row in items['body']:
            result.append(u'<tr>')
            for item in row:
                result.append(u'<td>')
                result.append(item)
                result.append(u'</td>')
            if items['select']['type'] == 'button':
                result.append(u'<td><button type="action" name="tablesel-row-button">SELECT</button></td>')
            else:
                result.append(u'<td><input type="checkbox" name="tablesel-header" /></td>')
            result.append(u'</tr>')
    return result

def _footer(this, options, items):
    result = [u'<tr>']
    if items['select']['position'] == 'left':
        if items['select']['type'] == 'button':
            result.append(u'<td>Select</td>')
        else:
            result.append(u'<td><input type="checkbox" name="tablesel-header" /></td>')
        for item in items['footer_list']:
            result.append(u'<td>')
            result.append(item)
            result.append(u'</td>')
    else:
        if items['select']['type'] == 'button':
            for item in items['footer_list']:
                result.append(u'<td>')
                result.append(item)
                result.append(u'</td>')
            result.append(u'<td>Select</td>')
        else:
            for item in items['footer_list']:
                result.append(u'<td>')
                result.append(item)
                result.append(u'</td>')
            result.append(u'<td><input type="checkbox" name="tablesel-header" /></td>')
    result.append(u'</tr>')
    return result
