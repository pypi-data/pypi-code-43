from typing import Any

from pydantic import BaseModel


class MongoModel(BaseModel):
    id: str

    def __init__(self, **data: Any) -> None:
        data['id'] = str(data.get('_id'))
        super().__init__(**data)
