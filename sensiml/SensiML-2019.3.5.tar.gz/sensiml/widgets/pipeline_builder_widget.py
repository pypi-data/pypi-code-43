from ipywidgets import (
    Layout,
    Button,
    VBox,
    HBox,
    Dropdown,
    Checkbox,
    Label,
    widgets,
    HTML,
)
from sensiml.widgets.base_widget import BaseWidget
import qgrid
from pandas import DataFrame


class PipelineBuilderWidget(BaseWidget):
    def _refresh(self, b=None):
        if not self._dsk:
            raise Exception("Must have dsk ")

        if not self._dsk.project:
            raise Exception("Must have active project")

        if not self._dsk.pipeline:
            raise Exception("Must have active pipeline.")

    def _clear(self):
        for index, subtype in enumerate(self._w_subtype):
            subtype.children[0].value = False

    def _on_button_clicked(self, change=None):
        active_subtypes = get_active_subtypes(self._w_subtypes)
        subtype_list = build_subtype_list(self._dsk, active_subtypes)

        self._widget_render_space.value = generate_pipeline_html_call(
            self._dsk, subtype_list
        )

    def create_widget(self):

        self._b_run = Button(
            icon="play",
            description="Generate Call",
            layout=Layout(width="98%", align_self="flex-end"),
        )

        self._b_run.on_click(self._on_button_clicked)
        self._refresh()

        self._w_subtypes = build_widgets(self._dsk)

        self._widget_render_space = HTML()

        return VBox(self._w_subtypes + [self._b_run, self._widget_render_space])


def get_subtype_defaults(dsk, subtype):
    fgs = dsk.list_functions(
        functype="Feature Generator", subtype=subtype, kp_functions=True
    ).df.NAME
    params = {}
    for fg in fgs:
        for param in dsk.functions._function_list[fg].input_contract:
            if param["name"] in ["input_data", "columns", "group_columns"]:
                continue
            params[param["name"]] = param["type"]

    return params


def build_widgets(dsk):
    w_subtypes = []
    fg_subtypes = dsk.list_functions(functype="Feature Generator").df.SUBTYPE.unique()
    for subtype in fg_subtypes:
        subtype_and_params = [widgets.Checkbox(value=False, description=subtype)]
        w_subtypes.append(HBox(subtype_and_params))
    return w_subtypes


def get_active_subtypes(w_subtype):
    active = []
    for subtype in w_subtype:
        if subtype.children[0].value:
            active.append(subtype.children[0].description)
    return active


def build_pipeline(dsk, active_subtypes):
    subtype_list = []
    for subtype in active_subtypes:
        tmp_dict = {"subtype_call": subtype}
        subtype_list.append(tmp_dict)

    dsk.pipeline.add_feature_generator(
        subtype_list, function_defaults={"columns": dsk.pipeline.data_columns}
    )


def build_subtype_list(dsk, active_subtypes):
    subtype_list = []
    for subtype in active_subtypes:
        tmp_dict = {
            "subtype_call": subtype,
            "params": get_subtype_defaults(dsk, subtype),
        }
        subtype_list.append(tmp_dict)

    return subtype_list


def generate_pipeline_call(dsk, subtype_list):

    return "dsk.pipeline.add_feature_generator(\n\t\t{0},\n\t\t function_defaults={{'columns':{1}}})".format(
        ",\n\t\t".join([str(x) for x in subtype_list]), dsk.pipeline.data_columns
    )


def generate_pipeline_html_call(dsk, subtype_list):

    return "dsk.pipeline.add_feature_generator(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{0},<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;function_defaults={{'columns':{1}}})".format(
        ",<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;".join(
            [str(x) for x in subtype_list]
        ),
        dsk.pipeline.data_columns,
    )
