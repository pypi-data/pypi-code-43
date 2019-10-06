from typing import List, Tuple

def odd_even_split(data:List)->Tuple[List, List]:
    """Return given list split into even and odds elements.
        data:List, list of data to split.
    """
    return data[::2], data[1::2]