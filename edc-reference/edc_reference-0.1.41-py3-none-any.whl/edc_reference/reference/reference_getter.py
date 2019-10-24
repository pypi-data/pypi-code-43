from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from ..site_reference import site_reference_configs


class ReferenceGetterError(Exception):
    pass


class ReferenceObjectDoesNotExist(Exception):
    pass


class ReferenceGetter:
    """A class that gets the reference model instance for a given
    model or attributes of the model.

    See also ReferenceModelMixin.
    """

    def __init__(
        self,
        name=None,
        field_name=None,
        model_obj=None,
        visit_obj=None,
        subject_identifier=None,
        report_datetime=None,
        visit_schedule_name=None,
        schedule_name=None,
        visit_code=None,
        visit_code_sequence=None,
        timepoint=None,
        create=None,
    ):
        self._object = None
        self.created = None
        self.value = None
        self.has_value = False

        self.create = create
        self.field_name = field_name

        if model_obj:
            try:
                # given a crf model as model_obj
                self.report_datetime = model_obj.visit.report_datetime
                self.subject_identifier = model_obj.visit.subject_identifier
                self.visit_schedule_name = model_obj.visit.visit_schedule_name
                self.schedule_name = model_obj.visit.schedule_name
                self.visit_code = model_obj.visit.visit_code
                self.visit_code_sequence = model_obj.visit.visit_code_sequence
                self.timepoint = model_obj.visit.timepoint
                self.name = model_obj.reference_name
            except AttributeError:
                # given a visit model as model_obj
                self.subject_identifier = model_obj.subject_identifier
                self.report_datetime = model_obj.report_datetime
                self.visit_schedule_name = model_obj.visit_schedule_name
                self.schedule_name = model_obj.schedule_name
                self.visit_code = model_obj.visit_code
                self.visit_code_sequence = model_obj.visit_code_sequence
                self.timepoint = model_obj.timepoint
                self.name = model_obj.reference_name
        elif visit_obj:
            self.name = name
            self.subject_identifier = visit_obj.subject_identifier
            self.report_datetime = visit_obj.report_datetime
            self.visit_schedule_name = visit_obj.visit_schedule_name
            self.schedule_name = visit_obj.schedule_name
            self.visit_code = visit_obj.visit_code
            self.visit_code_sequence = visit_obj.visit_code_sequence
            self.timepoint = visit_obj.timepoint
        else:
            # given only the attrs
            self.name = name
            self.subject_identifier = subject_identifier
            self.report_datetime = report_datetime
            self.visit_schedule_name = visit_schedule_name
            self.schedule_name = schedule_name
            self.visit_code = visit_code
            self.visit_code_sequence = visit_code_sequence
            self.timepoint = timepoint

        reference_model = site_reference_configs.get_reference_model(name=self.name)
        self.reference_model_cls = django_apps.get_model(reference_model)

        # note: updater needs to "update_value"
        self.value = getattr(self.object, "value")
        self.has_value = True
        setattr(self, self.field_name, self.value)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}({self.name}.{self.field_name}',"
            f"'{self.subject_identifier},{self.report_datetime}"
            f") value={self.value}, has_value={self.has_value}>"
        )

    @property
    def object(self):
        """Returns a reference model instance.
        """
        if not self._object:
            self.created = False
            opts = dict(
                **self.required_options,
                **{k: v for k, v in self.visit_options.items() if v is not None},
            )
            try:
                self._object = self.reference_model_cls.on_site.get(**opts)
            except ObjectDoesNotExist as e:
                if self.create:
                    self._object = self.create_reference_obj()
                    self.created = True
                else:
                    raise ReferenceObjectDoesNotExist(f"{e}. Using {opts}")
        return self._object

    @property
    def required_options(self):
        """Returns a dictionary of query options required for both
        get and create.
        """
        return dict(
            identifier=self.subject_identifier,
            model=self.name,
            report_datetime=self.report_datetime,
            field_name=self.field_name,
        )

    @property
    def visit_options(self):
        """Returns a dictionary of query options of the visit attrs.
        """
        return dict(
            visit_schedule_name=self.visit_schedule_name,
            schedule_name=self.schedule_name,
            visit_code=self.visit_code,
            visit_code_sequence=self.visit_code_sequence,
            timepoint=self.timepoint,
        )

    def create_reference_obj(self):
        """Returns a newly create reference instance.

        Note: updater needs to "update_value".
        """
        if {k: v for k, v in self.visit_options.items() if v is None}:
            raise ReferenceGetterError(
                f"Unable to create a reference instance. "
                f"Null values for visit attrs not allowed. "
                f"Got {self.visit_options}."
            )
        return self.reference_model_cls.objects.create(
            **self.required_options, **self.visit_options
        )
