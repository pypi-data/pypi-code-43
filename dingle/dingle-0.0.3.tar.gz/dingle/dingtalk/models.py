# -*- coding: utf-8 -*-
import typing
import dataclasses


class BaseModel(object):
    def asdict(self):
        return dataclasses.asdict(self)


def convert_to_dict(obj_list):
    if isinstance(obj_list, (list, tuple)):
       return [i.asdict() if isinstance(i, BaseModel) else i\
               for i in obj_list]
    else:
       return obj_list.asdict() if isinstance(obj_list, BaseModel)\
           else obj_list


@dataclasses.dataclass
class FormComponentProp(BaseModel):
    id: str
    label: str
    unit: str
    placeholder: str = ""
    required: bool = True


@dataclasses.dataclass
class FormComponent(BaseModel):
    component_name: str
    props: typing.List[FormComponentProp] =\
           dataclasses.field(default_factory=list)


@dataclasses.dataclass
class ProcessInstanceApprover(BaseModel):
    user_ids: typing.List[str]
    ask_action_type: str = "NONE"


@dataclasses.dataclass
class FormComponentValue(BaseModel):
    name: str
    value: str
    ext_value: str = ""


@dataclasses.dataclass
class ProcessInstanceApprover(BaseModel):
    user_ids: typing.List[str]
    task_action_type: str

