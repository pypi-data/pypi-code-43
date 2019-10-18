from ..models.base import BaseModel


class Subject(BaseModel):
    def __init__(self, *args, **kwargs):
        self.uid = None
        self.name = None  # 必填*
        self.number = None  # 必填*
        self.school = None
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
