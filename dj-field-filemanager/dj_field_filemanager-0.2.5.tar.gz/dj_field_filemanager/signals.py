from django.db import transaction
from django.db.models.signals import post_delete


def get_subclasses(cls):
    """
    Returns all not abstract classes
    """
    result = []
    classes_to_inspect = [cls]
    while classes_to_inspect:
        class_to_inspect = classes_to_inspect.pop()
        for subclass in class_to_inspect.__subclasses__():
            if subclass not in result:
                if not subclass._meta.abstract:
                    result.append(subclass)
                else:
                    classes_to_inspect.append(subclass)
    return result


def document_model_post_delete(sender, instance, **kwargs):
    """
    call deferred_post_delete once the transaction commit is successful
    """
    transaction.on_commit(instance.deferred_post_delete)


def document_parent_post_delete(sender, instance, **kwargs):
    """
    call DocumentModel.check_delete_parent_folder once the transaction commit
    is successful
    """
    def deferred():
        from .models import DocumentModel
        DocumentModel.check_delete_parent_folder(instance)
    transaction.on_commit(deferred)


def attach_signals():
    """
    Attaches required signals to DocumentModel classes and it's parent model
    for delete the required files and folders.
    """
    from .models import DocumentModel
    parents = set()
    for subclass in get_subclasses(DocumentModel):
        post_delete.connect(document_model_post_delete, subclass)
        parents.add(subclass._meta.get_field(subclass.get_parent()).related_model)

    for parent in parents:
        post_delete.connect(document_parent_post_delete, parent)
