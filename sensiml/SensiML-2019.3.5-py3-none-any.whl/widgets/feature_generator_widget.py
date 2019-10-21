from ipywidgets import Layout, Button, VBox, HBox, Dropdown, Checkbox, Label, widgets, HTML, GridspecLayout
from sensiml.widgets.base_widget import BaseWidget
import qgrid
from pandas import DataFrame


class FeatureGeneratorWidget(BaseWidget):

    def _refresh(self):
        if not self._dsk:
            raise Exception("Must have dsk.")

        if not self._dsk.project:
            raise Exception("Must have active project.")

        if not self._dsk.pipeline:
            raise Exception("Must have active pipeline.")

        fill_widgets_grid(self._dsk, self._w_grid)

    def hide(self):
        self._w_grid.layout.height = '0px'

    def show(self):
        self._w_grid.layout.height='auto'

    def _clear(self):
        for index, subtype in enumerate(self._w_subtype):
            subtype.children[0].value = False

    def get_fature_generator(self):
        subtype_list = get_active_subtypes(self._w_grid)

        feature_generators = self._dsk.pipeline.add_feature_generator([{'subtype_call': str(x)} for x in subtype_list],
                                                 function_defaults={'columns':self._dsk.pipeline.data_columns},
                                                 return_generator_set=True)._to_dict()

        feature_generators['outputs'] = ['temp.generator_set0', 'temp.features.generator_set0']

        return feature_generators

    def create_widget(self):

        self._w_grid = build_widgets_grid()

        return self._w_grid

def get_subtype_defaults(dsk, subtype):
    fgs = dsk.list_functions(functype='Feature Generator',
                             subtype=subtype, kp_functions=True).df.NAME
    params = {}
    for fg in fgs:
        for param in dsk.functions._function_list[fg].input_contract:
            if param['name'] in ['input_data', 'columns', 'group_columns']:
                continue
            params[param['name']] = param['type']

    return params


def build_widgets_grid(width=3, height=6):
    grid = GridspecLayout(height, width)
    for row in range(height):
        for col in range(width):
            grid[row, col] = widgets.Checkbox(value=False,
                                              description='{}{}'.format(row,col),
                                              layout=Layout(visibility='hidden')
                                              )

    return grid


def fill_widgets_grid(dsk, grid):

    fg_subtypes = dsk.list_functions(
        functype='Feature Generator').df.SUBTYPE.unique()

    index = 0
    for row in range(grid.n_rows):
        for col in range(grid.n_columns):
            if index >= len(fg_subtypes):
                continue
            grid[row, col].value = False
            grid[row, col].description = fg_subtypes[index]
            grid[row, col].layout.visibility = 'visible'
            index += 1

    return grid


def get_active_subtypes(grid):
    active = []
    for row in range(grid.n_rows):
        for col in range(grid.n_columns):
            if grid[row, col].value:
                active.append(grid[row, col].description)

    return active


def build_pipeline(dsk, active_subtypes):
    subtype_list = []
    for subtype in active_subtypes:
        tmp_dict = {'subtype_call': subtype}
        subtype_list.append(tmp_dict)

    dsk.pipeline.add_feature_generator(subtype_list, function_defaults={
                                       'columns': dsk.pipeline.data_columns})


def build_subtype_list(dsk, active_subtypes):
    subtype_list = []
    for subtype in active_subtypes:
        tmp_dict = {'subtype_call': subtype,
                    'params': get_subtype_defaults(dsk, subtype)}
        subtype_list.append(tmp_dict)

    return subtype_list
