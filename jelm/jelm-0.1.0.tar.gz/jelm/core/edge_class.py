from typing import Optional


class Edge:

    def __init__(self,
                 source: str,
                 target: str,
                 id: Optional[str] = None,
                 attributes: Optional[dict] = None):

        self.source = source
        self.target = target
        self.id = id
        self.attributes = attributes or {}

    def get_dict(self) -> dict:
        optionals = {
            k: self.__getattribute__(k)
            for k in ['id', 'attributes'] if self.__getattribute__(k)
        }
        return {
            'type': 'edge',
            'source': self.source,
            'target': self.target,
            **optionals
        }
