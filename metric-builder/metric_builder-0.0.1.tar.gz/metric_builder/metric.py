from inspect import getmembers, isfunction

from jinja2 import Environment, BaseLoader

from metric_builder import template_filters


def get_custom_template_filters():
    return [f for f in getmembers(template_filters) if isfunction(f[1])]


class Metric:
    def __init__(self, query, reader):
        self.query = query
        self.reader = reader

        self.jinja_env = Environment(autoescape=True, loader=BaseLoader())
        self.__load_custom_filters()

    def fetch(self, reference_time):
        """Interpolate and execute the defined function with the passed in reader object"""
        query = self.__interpolate_query(reference_time)
        return self.reader.execute(query)

    def __load_custom_filters(self):
        """Load all custom template filters and add them to the jinja environment"""
        custom_filters = get_custom_template_filters()
        for f in custom_filters:
            self.jinja_env.filters[f[0]] = f[1]

    def __interpolate_query(self, reference_time):
        template = self.jinja_env.from_string(self.query)
        return template.render(reference_time=reference_time)
