# -*- coding: utf-8 -*-

from copy import deepcopy
from collections import OrderedDict, defaultdict

from terminaltables import SingleTable, DoubleTable, AsciiTable

from .behaviors import NA_VALUE, ArithmeticBehavior, Variables, List
from .colors import bold


TABLE_TYPES = {"ascii": AsciiTable, "single": SingleTable, "double": DoubleTable}


class ReportingSession(object):
    def __init__(self):
        self.reports = OrderedDict()
        self.configs = {}

    def xdist_update(self, another_session):
        for report, data in another_session.reports.items():
            self.reports.setdefault(report, {})
            self.reports[report].setdefault("metrics", [])

            self.reports[report]["metrics"] += data["metrics"]

        # Should be the same on each node
        self.configs.update(another_session.configs)

    def configure(self, report, config):
        self.configs[report] = deepcopy(config)

    def add(self, report, variables, **kwargs):
        self.reports.setdefault(report, {})
        self.reports[report].setdefault("metrics", [])

        for metric, value in kwargs.items():
            self.reports[report]["metrics"].append((variables, metric, value))

    def prepare_metrics(self, metrics, config):
        display_total = config.get("display_total", False)
        columns = config.get("columns", [])
        order_by = config.get("order_by", [])

        # Group by variables
        metrics_by_vars = OrderedDict()
        default_columns = []

        if order_by:
            orders = [
                (
                    -1 if order[0] == "-" else 1,
                    order[1:] if order.startswith("-") else order,
                )
                for order in order_by
            ]
            for sign, order in reversed(orders):
                metrics = sorted(metrics, key=lambda k: k[0][order], reverse=sign == -1)

        for variables, metric, value in metrics:
            key = tuple(sorted(variables.items()))

            default_columns.append(metric)
            metrics_by_vars.setdefault(key, OrderedDict())
            metrics_by_vars[key].setdefault(metric, [])
            metrics_by_vars[key][metric].append(value)

        # Remove duplicates columns
        default_columns = [List(c) for c in OrderedDict.fromkeys(default_columns)]

        columns = [Variables("variables")] + (columns or default_columns)

        lines = [[bold(c.__unicode__()) for c in columns]]

        arithmetic_columns = defaultdict(list)

        # Apply configured behavior or the default one
        for variables, metrics in metrics_by_vars.items():
            line = [columns[0](variables)]
            for col in columns[1:]:
                metric = col.fieldname
                behavior = col

                values = metrics.get(metric)
                if values:
                    line.append(behavior(values))

                    if isinstance(behavior, ArithmeticBehavior):
                        arithmetic_columns[col].append(behavior(values))
                else:
                    line.append(NA_VALUE)

            lines.append(line)

        if display_total:
            lines.append([])  # One empty line

            total_line = ["total"]
            for col in columns[1:]:
                values = arithmetic_columns.get(col)
                if values:
                    total_sum = sum([v for v in values if v != NA_VALUE])
                    total_line.append(total_sum)
                else:
                    total_line.append(NA_VALUE)

            lines.append(total_line)

        return lines

    def display_report(self, terminalreporter, report_name, data):
        title = u" {} ".format(report_name)
        config = self.configs.get(report_name, {})
        table_data = self.prepare_metrics(data["metrics"], config)

        table_class = TABLE_TYPES[config.get("table_type", "single")]

        table = table_class(table_data, title=title)

        report_display_callback = config.get("report_display_callback")
        if report_display_callback:
            report_display_callback(table_data, title)

        terminalreporter.write(table.table)

    def display(self, terminalreporter):
        if not self.reports:
            return

        terminalreporter.section("reporting plugin")

        for report_name, data in self.reports.items():
            self.display_report(terminalreporter, report_name, data)
            terminalreporter.line("")


class ReportingConfig(object):
    def __init__(self, session):
        self.session = session
