from ..models.base import BaseModel


class Subject(BaseModel):
    uid = None
    name = None  # 必填*
    number = None  # 必填*
    school = None

    def __init__(self, *args, **kwargs):
        super(Subject, self).__init__(*args, **kwargs)
        self.required_filed = ['name', 'number']

    @property
    def nirvana_data(self):
        data = {
            "name": self.name,
            "num": self.number,
            "school": self.school
        }
        return data
