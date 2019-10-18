
"""
base_verb.py

Defines the abstract class for all BXML verbs

@author Jacob Mulford
@copyright Bandwidth INC
"""

from abc import ABC, abstractmethod


class AbstractBxmlVerb(ABC):

    @abstractmethod
    def to_xml(self):
        """
        Converts the class into its xml representation

        :return str: The string xml representation
        """
        pass
