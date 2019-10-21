from ipywidgets import widgets
import qgrid
from ipywidgets import (
    Layout,
    Button,
    HBox,
    VBox,
    Box,
    HTML,
    FloatText,
    Tab,
    Textarea,
    Dropdown,
    Label,
    IntSlider,
    Checkbox,
    Text,
    Button,
    SelectMultiple,
)
from IPython.display import display
from ipywidgets import IntText
from sensiml.widgets.base_widget import BaseWidget, button_handling
from sensiml.base.exceptions import QueryExistsException
from six import text_type
import numpy as np
from IPython.display import display
from bqplot import OrdinalScale, LinearScale, Bars, Lines, Axis, Figure
from sensiml.widgets.renderers import WidgetAttributeRenderer
from pandas import DataFrame


def get_item(x, index, default=None):
    try:
        return x[index]
    except:
        return default


class QueryWidget:
    def __init__(self, dsk):
        self._dsk = dsk
        self._items = {"query_select": ""}
        self._stats = None

    def _enable_buttons(self):

        self._add_query.disabled = False
        self._update_query.disabled = False
        self._delete_query.disabled = False

    def _disable_buttons(self):

        self._add_query.disabled = True
        self._update_query.disabled = True
        self._delete_query.disabled = True

    @button_handling
    def on_add_query_button_clicked(self, b):

        if self.add_query(create=True, force=False):
            self.query_widget_tab.selected_index = 0

    @button_handling
    def on_update_query_button_clicked(self, b):
        if self._query_select.value:
            self.add_query(force=True)

    @button_handling
    def on_delete_query_button_clicked(self, b):
        if self._dsk is None:
            return
        if self._dsk.project is None:
            return
        if self._query_select.value:
            query = self._dsk.project.queries.get_query_by_name(
                self._query_select.value
            )
            query.delete(renderer=self.renderer)

        self._refresh()

    def add_query(self, create=False, force=False):
        if self._dsk is None:
            return
        if self._dsk.project is None:
            return
        if self._query_select.options == self._query_name_text.value and force == False:
            return

        self.populate_items(populate_create=create)
        query_name = self._items.get("query_name", None)
        segmenter_name = self._items.get("segmenter_name", None)
        label_column = self._items.get("label_column")
        metadata_columns = self._items.get("metadata_columns", None)
        sensor_columns = self._items.get("sensor_columns", None)
        metadata_filter = self._items.get("metadata_filter", "")

        if not segmenter_name:
            self.renderer.render("No segmenter specified")
            return

        # reverse lookup of segmenter id
        segmenters = self._dsk.list_segmenters()
        segmenter_id = int(
            segmenters[segmenters["name"] == self._items["segmenter_name"]][
                "id"
            ].values[0]
        )

        if not query_name:
            self.renderer.render("No query name specified")
            return

        if label_column in metadata_columns:
            self.renderer.render("Label Column cannot be part of metadata columns.")
            return

        if not metadata_columns:
            self.renderer.render("No Metadata Columns Specified")
            return
        if isinstance(metadata_columns, str):
            metadata_columns = metadata_columns.split(",")

        if not sensor_columns:
            self.renderer.render("No Sensor Columns Specified")
            return

        if isinstance(sensor_columns, str):
            sensor_columns = sensor_columns.split(",")

        try:
            self.renderer.render("Creating Query.")
            self.query = self._dsk.create_query(
                query_name,
                columns=sorted(sensor_columns),
                metadata_columns=[m for m in metadata_columns if m != label_column],
                segmenter=segmenter_id,
                metadata_filter=metadata_filter,
                label_column=label_column,
                force=force,
                renderer=self.renderer,
            )
            self.renderer.render("Query Created.")

        except QueryExistsException:
            self.renderer.render("Query Already Exists. Select force to overwrite.")
            return None

        if create:
            self._query_select.options = sorted(
                self._query_select.options + (query_name,), key=lambda s: s.lower()
            )
            self._query_select.value = query_name
            self._query_name_text.value = ""
            self._metadata_filter_text_create.value = ""
            self._segmenter_select_create.value = ""

        else:
            self._query_select.options = sorted(
                self._query_select.options, key=lambda s: s.lower()
            )
            self._query_select.value = query_name
            self.update_statistics(self.query)

        return True

    @button_handling
    def update_statistics(self, query=None, plot_type="segments"):

        if query is not None:
            try:
                self.renderer.render("Getting Query Statistics.")
                self._stats = query.statistics_segments(renderer=self.renderer)
                self.renderer.render("Revieved Query STatistics.")
                self.renderer.render("")

            except:
                self._graph.marks = []
                self._graph.axes = []
                self._graph.title = ""
                return

        else:
            query = self.query

        data = []
        Labels = []
        counts = []
        segments = []
        stacked_data = []

        g = self._stats.groupby(query.label_column)

        for tmp_df in g:
            Labels.append(tmp_df[0])
            data.append(sorted(list(tmp_df[1]["Segment Length"]), reverse=True))
            counts.append((tmp_df[1]["Segment Length"]).sum())
            segments.append(tmp_df[1]["Segment Length"].shape[0])

        num_classes = len(data)
        max_segments = max(segments)

        # Stacked bar Chart
        for j in range(max_segments):
            stacked_data.append([get_item(data[i], j, 0) for i in range(num_classes)])

        x_ord = OrdinalScale()
        y_lin = LinearScale(min=0.0)

        ax_x = Axis(scale=x_ord, tick_values=Labels, tick_rotate=10)
        ax_y = Axis(
            scale=y_lin, orientation="vertical", label=plot_type, label_offset="60px"
        )

        if plot_type == "samples":
            bar = Bars(
                x=Labels,
                y=counts,
                color_mode="group",
                type="stacked",
                scales={"x": x_ord, "y": y_lin},
            )

        elif plot_type == "segments":
            bar = Bars(
                x=Labels,
                y=segments,
                color_mode="group",
                type="stacked",
                scales={"x": x_ord, "y": y_lin},
            )

        elif plot_type == "samples_stacked":
            bar = Bars(
                x=Labels,
                y=stacked_data,
                color_mode="group",
                type="stacked",
                scales={"x": x_ord, "y": y_lin},
            )

        else:
            raise Exception("Plot Type Not Supported.")

        self._graph.marks = [bar]
        self._graph.axes = [ax_x, ax_y]
        self._graph.title = ""

    def _refresh(self):
        self._dsk.project.refresh()
        self._stats = None

        sensor_items = []
        metadata_items = []
        queries = []

        self._graph.marks = []
        self._graph.axes = []
        self._graph.title = ""

        segmenters = self._dsk.list_segmenters()
        if segmenters is None:
            self.renderer.render("No queryable data added to this project")
            segmenters = []
        else:
            segmenters = sorted(
                list(segmenters["name"].values), key=lambda s: s.lower()
            )

        columns = self._dsk.project.columns()
        if columns is None:
            self.renderer.render("No schema associated with this project.")
            columns = []

        for column in sorted(columns):
            sensor_items.append(column)

        metadata_items = self._dsk.project.metadata_columns()
        if metadata_items is None:
            self.renderer.render("No metdata associated with this project")
            metadata_items = []

        label_items = []
        for label in self._dsk.project.label_columns():
            if label != "SegmentID":
                label_items.append(label)

        query_df = self._dsk.list_queries()
        if query_df is not None:
            for query in query_df["Name"].values:
                queries.append(query)

        self._segmenter_select.options = [""] + segmenters
        self._segmenter_select_create.options = [""] + segmenters
        self._segmenter_select.value = self._segmenter_select.options[0]
        self._label_column_select.options = label_items
        self._label_column_select_create.options = label_items

        self._metadta_items_mselect.options = metadata_items
        self._metadata_items_mselect_create.options = metadata_items
        for name in metadata_items:
            if name.lower() in ["subject", "subjects"]:
                self._metadata_items_mselect_create.value = [name]

        self._sensor_columns_mselector.options = sensor_items
        self._sensor_columns_mselector_create.options = sensor_items
        self._sensor_columns_mselector_create.value = sensor_items
        self._query_select.options = [""] + sorted(
            list(set(queries)), key=lambda s: s.lower()
        )
        self._query_name_text.value = ""
        self._metadata_filter_text_create.value = ""
        self._metadata_filter_text.value = ""
        self.populate_items()

        project_stats, _ = self._dsk.project.statistics()
        self._w_project_explorer.df = project_stats

        return True

    def populate_items(self, populate_create=False):

        self._items["sensor_columns"] = self._sensor_columns_mselector.value
        self._items["metadata_columns"] = self._metadta_items_mselect.value
        self._items["label_column"] = self._label_column_select.value
        self._items["segmenter_name"] = self._segmenter_select.value
        self._items["query_name"] = self._query_select.value
        self._items["query_select"] = self._query_select.value
        self._items["metadata_filter"] = self._metadata_filter_text.value

        if populate_create:
            self._items["sensor_columns"] = self._sensor_columns_mselector_create.value
            self._items["metadata_columns"] = self._metadata_items_mselect_create.value
            self._items["label_column"] = self._label_column_select_create.value
            self._items["segmenter_name"] = self._segmenter_select_create.value
            self._items["query_name"] = self._query_name_text.value
            self._items["metadata_filter"] = self._metadata_filter_text_create.value

    def populate_query(self, change=None):
        self.populate_items()

        self.query = self._dsk.project.queries.get_query_by_name(
            self._items["query_select"]
        )

        if self.query:
            qdict = self.query._to_dict()
            self._qdict = qdict
            seg = self._dsk.list_segmenters()

            self._sensor_columns_mselector.value = qdict["sensor_columns"]
            self._metadta_items_mselect.value = qdict["metadata_columns"]
            self._label_column_select.value = qdict["label_column"]
            self._metadata_filter_text.value = qdict["metadata_filter"]

            if list(seg[seg["id"] == qdict["segmenter_id"]]["name"]):
                self._segmenter_select.value = list(
                    seg[seg["id"] == qdict["segmenter_id"]]["name"]
                )[0]
            else:
                self.renderer.render(
                    "Error. Query {} is associated with a Segmenter that no longer exists!".format(
                        self._items["query_select"]
                    )
                )
                return

            self.populate_items()

            self.update_statistics(self.query)

    def switch_plots(self, change=None):

        if self._stats is not None:
            self.update_statistics(None, change["new"])

    def create_widget(self, name=""):
        # refresh the project so that the most up to date values are shown

        self._query_name_text = Text(description="Name")
        self._query_select = Dropdown(description="Name")
        self._segmenter_select = Dropdown(description="Session")
        self._plot_type = Dropdown(
            description="Plot",
            options=["segments", "samples", "samples_stacked"],
            value="segments",
        )
        self._segmenter_select_create = Dropdown(description="Session")
        self._label_column_select = Dropdown(description="Label")
        self._label_column_select_create = Dropdown(description="Label")
        self._metadta_items_mselect = SelectMultiple(description="Metadata")
        self._metadata_items_mselect_create = SelectMultiple(description="Metadata")
        self._sensor_columns_mselector = SelectMultiple(description="Sources")
        self._sensor_columns_mselector_create = SelectMultiple(description="Sources")
        self._metadata_filter_text = Text(description="Query Filter")
        self._metadata_filter_text_create = Text(description="Query Filter")
        self._add_query = Button(
            icon="plus",
            description="Add",
            tooltip="Create New Query",
            layout=Layout(width="98%", allign_item="center"),
        )
        self._update_query = Button(
            icon="upload",
            description="Update",
            tooltip="Update Query",
            layout=Layout(width="98%", allign_item="center"),
        )
        self._delete_query = Button(
            icon="trash",
            description="Delete",
            tooltip="Delete Query",
            layout=Layout(width="98%", allign_item="center"),
        )

        self._w_project_explorer = qgrid.show_grid(
            DataFrame({"capture_name": [""]}),
            grid_options={
                "rowHeight": 32,
                "maxVisibleRows": 30,
                "minVisibleRows": 6,
                "editable": False,
                "defaultColumnWidth": 100,
                "forceFitColumns": True,
                "sortable": True,
                "filterable": True,
            },
            column_options={"minWidth": 30},
            column_definitions={"index": {"width": 30}, "capture_name": {"width": 350}},
        )

        self._add_query.on_click(self.on_add_query_button_clicked)
        self._update_query.on_click(self.on_update_query_button_clicked)
        self._delete_query.on_click(self.on_delete_query_button_clicked)

        self._graph = Figure(
            marks=[],
            axes=[],
            title="",
            legend_location="bottom-right",
            background_style={"fill": "white"},
            fig_margin={"top": 10, "bottom": 30, "left": 100, "right": 0},
        )
        self._graph.layout.height = text_type("325px")
        self._graph.layout.width = "70%"

        self._query_select.observe(self.populate_query, "value")
        self._plot_type.observe(self.switch_plots, "value")

        self._widget_render_space = HTML()

        self.renderer = WidgetAttributeRenderer(self._widget_render_space, "value")

        self.query_widget_tab = Tab(
            [
                HBox(
                    [
                        VBox(
                            [
                                self._query_select,
                                self._segmenter_select,
                                self._label_column_select,
                                self._metadta_items_mselect,
                                self._sensor_columns_mselector,
                                self._metadata_filter_text,
                                self._plot_type,
                                HBox([self._delete_query, self._update_query]),
                            ]
                        ),
                        self._graph,
                    ]
                ),
                HBox(
                    [
                        VBox(
                            [
                                self._query_name_text,
                                self._segmenter_select_create,
                                self._label_column_select_create,
                                self._metadata_items_mselect_create,
                                self._sensor_columns_mselector_create,
                                self._metadata_filter_text_create,
                                self._add_query,
                            ]
                        )
                    ]
                ),
                HBox([self._w_project_explorer]),
            ]
        )

        self.query_widget = VBox([self.query_widget_tab, self._widget_render_space])

        self.query_widget_tab.set_title(0, "Select/Modify Query")
        self.query_widget_tab.set_title(1, "Create New Query")
        self.query_widget_tab.set_title(2, "Project Explorer")

        if self._dsk:
            if self._refresh():
                self.populate_query()

        return self.query_widget
