from rox.core.context.merged_context import MergedContext
from rox.core.impression.models.reporting_value import ReportingValue


class Variant(object):
    def __init__(self, default_value, options = []):
        options = list(options)
        if default_value not in options:
            options.append(default_value)

        self.options = options
        self.default_value = default_value

        self.condition = None
        self.parser = None
        self.global_context = None
        self.impression_invoker = None
        self.experiment = None
        self.name = None

    def set_for_evaluation(self, parser, experiment, impression_invoker):
        if experiment is not None:
            self.experiment = experiment
            self.condition = experiment.condition
        else:
            self.experiment = None
            self.condition = ''

        self.parser = parser
        self.impression_invoker = impression_invoker

    def set_context(self, global_context):
        self.global_context = global_context

    def set_name(self, name):
        self.name = name

    def get_value(self, context=None):
        return self._get_value(context, none_instead_of_default=False)

    def _get_value(self, context, none_instead_of_default):
        return_value = None if none_instead_of_default else self.default_value
        merged_context = MergedContext(self.global_context, context)

        if self.parser is not None and self.condition:
            evaluation_result = self.parser.evaluate_expression(self.condition, context=merged_context)
            if evaluation_result is not None and evaluation_result.string_value():
                value = evaluation_result.string_value()
                if value is not None:
                    return_value = value

        if self.impression_invoker is not None:
            self.impression_invoker.invoke(ReportingValue(self.name, return_value), self.experiment, merged_context)

        return return_value

    def __repr__(self):
        return "%s(%r, %r)" % (type(self).__name__, self.default_value, self.options)

    def __str__(self):
        return "%s(%s, %s, name=%s, condition=%s)" % (type(self).__name__, self.default_value, self.options, self.name, self.condition)
