from typing import List, Optional, Tuple


def get_meta_value(
    category: str, meta: List[object]
) -> Tuple[bool, Optional[int], List]:
    """
    The business logic is:
        * We will get an array, meta
        * meta will either be the empty array, or have >= 1 element
            * if empty, the service is disabled
            * if nonempty, get meta[0]
            * meta[0].value is the usable value
            * CAN IGNORE meta[0].enabled - will never be zero, per Yakiv
    """
    enabled, value, sub_groups = False, None, []
    if not meta:
        pass
        print("empty meta array: assuming service is disabled")
    else:
        try:
            meta_el = meta[0]
        except IndexError as e:
            print("Yakiv swore this would not happen", e)
            return enabled, value, sub_groups
        try:
            styleGuideMeta = meta_el["styleGuideMeta"]
        except KeyError as e:
            print("Meta element has no styleGuideMeta prop", e)
            return enabled, value, sub_groups

        try:
            value = int(styleGuideMeta["value"])
            enabled = True
        except KeyError as e:
            value = None

        try:
            sub_groups = styleGuideMeta["subGroup"]
            enabled = True
        except KeyError as e:
            sub_groups = []

        if value == None and sub_groups == []:
            enabled = True
            print("Value and subGroups aren't set, assuming simple on/off service")

    return enabled, value, sub_groups

