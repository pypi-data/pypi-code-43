from typing import Optional


class AbsentType:
    """
    Singleton class representing a property that is absent from
    a configuration.
    """
    # The singleton instance
    __instance: Optional['AbsentType'] = None

    # Create the instance the first time, then just return it
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __str__(self) -> str:
        return "Absent"


# Create the singleton instance for export
Absent = AbsentType()
