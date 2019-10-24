import mutations.fields
from goflow.runtime.models import WorkItem
from goflow.workflow.models import Transition

# Todos os Use Cases de Workflow

TupleField = mutations.fields.build_field_for("TupleField", tuple)
WorkItemField = mutations.fields.build_field_for("WorkItemField", WorkItem)
TransitionField = mutations.fields.build_field_for("TransitionField", Transition)


# class CustomValidator(ValidatorBase):
#     def __init__(self, func, *args, **kwargs):
#         self.func = func
#         super().__init__(*args, **kwargs)
#
#     def is_valid(self, *args, **kwargs):
#         return self.func(*args, **kwargs)


def mutation_workitem_status_config(mutation):
    """ Se numa mutação de Use Case de WorkFlow o status não é informado e há workflow associado,
        então tenta o status da activity associada ao workitem """

    if not mutation.status and mutation.workitem and \
            mutation.workitem.activity.status_update and mutation.workitem.activity.status_new:
        mutation.status = mutation.workitem.activity.status_new


def object_status_update(obj, status, save):
    if obj.status != status:
        obj.status = status
        if save:
            obj.save(update_fields=['status'])
            # obj.save()
    return obj


