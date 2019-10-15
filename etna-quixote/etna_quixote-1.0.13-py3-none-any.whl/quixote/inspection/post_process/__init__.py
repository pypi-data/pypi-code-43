from quixote.inspection import get_inspection_result


def ok_ko(checklist_entry: str = None):
    point = 0
    if all(get_inspection_result()["requirements"]):
        point = 1
    if checklist_entry:
        get_inspection_result()["checklist"][checklist_entry] = point
    else:
        get_inspection_result()["points"] = point


def grade_points(checklist_entry: str = None):
    point = 0
    for requirement in get_inspection_result()["requirements"]:
        if requirement[0]:
            point += requirement[2]
    if checklist_entry:
        get_inspection_result()["checklist"][checklist_entry] += point
    else:
        get_inspection_result()["points"] += point
