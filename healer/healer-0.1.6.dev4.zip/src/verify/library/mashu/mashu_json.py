from enum import Enum
from typing import Set
from dataclasses import dataclass
from mashumaro import DataClassJSONMixin

class PetType(Enum):
    CAT = 'CAT'
    MOUSE = 'MOUSE'

@dataclass(unsafe_hash=True)
class Pet(DataClassJSONMixin):
    name: str
    age: int
    pet_type: PetType

@dataclass
class Person(DataClassJSONMixin):
    first_name: str
    second_name: str
    age: int
    pets: Set[Pet]


tom = Pet(name='Tom', age=5, pet_type=PetType.CAT)
jerry = Pet(name='Jerry', age=3, pet_type=PetType.MOUSE)
john = Person(first_name='John', second_name='Smith', age=18, pets={tom, jerry})

dump = john.to_json()
person = Person.from_json(dump)
# person == john

Pet.from_json('{"name": "Tom", "age": 5, "pet_type": "CAT"}')
# Pet(name='Tom', age=5, pet_type=<PetType.CAT: 'CAT'>)
