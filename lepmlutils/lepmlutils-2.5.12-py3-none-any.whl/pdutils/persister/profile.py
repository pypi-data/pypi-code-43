from typing import List

# Profile represents metadata about a persisted dataFrame.
class Profile():
    def __init__(self, name: str, time_cols: List[str] = []):
        self.name = name
        self.time_cols = time_cols
    
    def has_time_cols(self) -> bool:
        return len(self.time_cols) > 0