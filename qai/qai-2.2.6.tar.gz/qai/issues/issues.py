import uuid


def make_issue(word: str,
               start: int,
               end: int,
               issue_type: str,
               score,
               description='',
               suggestions=[],
               subCategory=''):
    '''
    reference:
    https://qordoba.atlassian.net/wiki/spaces/HOME/pages/840368141/Content-AI
    '''
    _uuid = str(uuid.uuid4())
    if not description:
        description = f'"{word}" is correlated with {issue_type} language.'
    issue = {
        "issueId": _uuid,
        "issueType": issue_type,
        "from": start,
        "until": end,
        "score": score,
        "suggestions": suggestions,
        "description": description,
    }
    
    if subCategory:
        issue["meta"] = { 
            "subCategory": subCategory 
            }

    return issue
