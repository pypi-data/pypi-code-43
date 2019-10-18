from kaf_pas.k_one_c.models_unmanaged.nomenklatura import Nomenklatura
from one_c.models.entities import Entities


class KafEntities(Entities):

    def get_field(self, id, name):
        _entity = [_entity for _entity in self.entities if _entity.id == id]
        if len(_entity) == 0:
            return None
        else:
            field = [field for field in _entity[0].used_field() if field.name == name]
            if len(field) == 0:
                return None
            else:
                return field[0]
