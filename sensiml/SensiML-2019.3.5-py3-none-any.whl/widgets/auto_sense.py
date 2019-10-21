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
    Tab,
)
from sensiml.widgets.base_widget import BaseWidget
import qgrid
import json
from pandas import DataFrame
from sensiml.widgets.renderers import WidgetAttributeRenderer
from sensiml.widgets.feature_generator_widget import FeatureGeneratorWidget
import threading

autosense_metric_column = [
    "Accuracy",
    "Classifer Size(B)",
    "Num. Features",
    "Sensitivity",
    "f1-score",
]


class AutoSenseWidget(BaseWidget):
    def _get_query_list(self):
        q_list = self._dsk.list_queries()
        if q_list is not None:
            return [""] + list(q_list["Name"].values)
        else:
            return [""]

    def _on_button_clicked(self, b):

        self._b_run.disabled = True
        self._b_run.description = "RUNNING..."
        self._b_run.icon = ""
        self._w_project.disabled = True
        self._w_pipeline.disabled = True

        thread = threading.Thread(target=self._async_run_pipeline_optimizer)
        thread.start()

    def _on_stop_button_clicked(self, b):
        if self._dsk and self._dsk.pipeline:
            self._dsk.pipeline.stop_pipeline()
            self.renderer.render("Terminating Pipeline Execution")

    def _async_run_pipeline_optimizer(self):
        try:
            self._run_pipeline_optimizer()
            self._dsk._auto_sense_ran = True
        except:
            self._reset_optimizer_button()

        self._reset_optimizer_button()

    def _reset_optimizer_button(self):

        self._b_run.disabled = False
        self._b_run.description = "Optimize"
        self._b_run.icon = "play"
        self._w_project.disabled = False
        self._w_pipeline.disabled = False

    def _run_pipeline_optimizer(self):
        query_name = self._w_query.value
        segmenter = str(self._w_segment.value)
        seed_choice = str(self._w_seed.value)
        classifiers_sram = self._w_classifiers_sram.value
        iterations = self._w_iterations.value
        population_size = self._w_population_size.value
        mutation_rate = self._w_mutation_rate.value
        recreation_rate = self._w_recreation_rate.value
        survivor_rate = self._w_survivor_rate.value
        reset = self._c_reset.value
        allow_unk = self._c_allow_unk.value
        hierarchical_model = self._c_hierarchical_model.value
        balanced_data = self._c_balanced_data.value
        optimization_metric = self._w_optimization_metric.value.lower()
        demean_segments = self._c_strip_mean.value
        outlier_filter = self._c_outlier_filter.value
        if self._w_combine_labels.value:
            combine_labels = json.loads(self._w_combine_labels.value)
        else:
            combine_labels = None

        if not query_name:
            self.renderer.render("\nERROR: No query name specified!\n")
            return

        if self._dsk.pipeline is None:
            self.renderer.render(
                "\nERROR: Pipeline is not set, use: dsk.pipeline='Pipeline Name'!\n"
            )
            return

        validation_method = {
            "name": self._w_validation_method.value,
            "inputs": {
                "number_of_folds": self._w_number_folds.value,
                "validation_size": self._w_validation_size.value / 100,
                "test_size": 0.0,
                "metadata_name": self._w_validation_metadata.value,
            },
        }

        if optimization_metric == "f1-score":
            optimization_metric = "f1_score"

        params = {
            "iterations": iterations,
            "reset": reset,
            "population_size": population_size,
            "mutation_rate": mutation_rate,
            "recreation_rate": recreation_rate,
            "survior_rate": survivor_rate,
            "allow_unknown": allow_unk,
            "validation_method": validation_method,
            "balanced_data": balanced_data,
            "demean_segments": demean_segments,
            "outlier_filter": outlier_filter,
            "allow_hierarchical_model": hierarchical_model,
            "prediction_target(%)": {optimization_metric: 100},
            "hardware_target": {"classifiers_sram": classifiers_sram},
            "combine_labels": combine_labels,
        }

        add_windowing = False
        delta = None

        if segmenter == "Query Segmenter":
            query = self._dsk.project.queries.get_or_create_query(query_name)
            if (
                self._dsk.project.get_segmenters().loc[query.segmenter]["name"]
                == "Manual"
            ):
                self.renderer.render(
                    "\n\nERROR: This Query only has manually labeled segments associated with it!\n\tSelect a Windowing Segmenter to run this pipeline.\n"
                )
                return

        elif "Windowing" in segmenter:
            delta = self._w_window_size.value
            add_windowing = True

        else:
            self.renderer.render(
                "\n\nERROR: No segmentation algorithm was selected. Select a Segmenter to run this pipeline.\n"
            )
            return

        self._dsk.project.query_optimize()

        self._dsk.pipeline.reset()
        self._dsk.pipeline.set_input_query(query_name)

        if add_windowing:
            self._dsk.pipeline.add_transform(
                "Windowing", params={"window_size": delta, "delta": delta}
            )

        if seed_choice == "Custom Feature Generatorset":
            params[
                "generatorset"
            ] = self.custom_feature_generator.get_fature_generator()

        print("Auto Sense Params", params)
        self._dsk.pipeline.describe()

        self._clear_auto_sense_results()
        self.results, self.summary = self._dsk.pipeline.auto(
            {"seed": seed_choice, "params": params}, renderer=self.renderer
        )

        self.renderer.render("\nAutomation Pipeline Completed.")

        self._set_auto_sense_results()

    def _clear_auto_sense_results(self):
        self._w_results.df = DataFrame(
            [[0, 0, 0, 0, 0] for _ in range(5)], columns=autosense_metric_column
        )

    def _set_auto_sense_results(self):

        self._clear_auto_sense_results()

        if (
            self.summary is not None
            and isinstance(self.summary, dict)
            and isinstance(self.summary.get("fitness_summary", None), DataFrame)
        ):
            if "f1_score" not in self.summary["fitness_summary"].columns:
                self.summary["fitness_summary"]["f1_score"] = 0

            df_results = (
                self.summary["fitness_summary"][
                    [
                        "accuracy",
                        "classifiers_sram",
                        "features",
                        "sensitivity",
                        "f1_score",
                    ]
                ]
                .astype(int)
                .head()
            )
            df_results = df_results.rename(
                index=str, columns={"classifiers_sram": "Classifier Size (B)"}
            )
            df_results = df_results.rename(index=str, columns={"accuracy": "Accuracy"})
            df_results = df_results.rename(
                index=str, columns={"sensitivity": "Sensitivity"}
            )
            df_results = df_results.rename(index=str, columns={"f1_score": "f1-score"})
            df_results = df_results.rename(
                index=str, columns={"features": "Num. Features"}
            )

            self._w_results.df = df_results
        else:
            if isinstance(self.results, dict):
                self.renderer.render(
                    self.results.get("message", "").replace("\n", "<br>")
                )

    def _terminate_run(self, b):
        self._dsk.pipeline.stop_pipeline()

    def _select_seed(self, Name):
        if self._dsk and Name:
            self._w_seed_desc.value = self._dsk.seeds.get_seed_by_name(Name).description
            if Name == "Custom Feature Generatorset":
                self.custom_feature_generator.show()
            else:
                self.custom_feature_generator.hide()

    def _on_value_change(self, change):
        if self._dsk is None:
            return
        if self._dsk.pipeline and change["new"]:
            self._dsk.pipeline.reset()
            self._dsk.pipeline.set_input_query(change["new"])
            self._w_validation_metadata.options = [
                x
                for x in self._dsk.pipeline.group_columns
                if x not in [self._dsk.pipeline.label_column, "SegmentID"]
            ]
        else:
            self.renderer.render("No Pipeline Selected.")

    def _on_validation_method_change(self, change):
        def set_states_visible(widgets):
            for widget in widgets:
                widget.layout.visibility = "visible"
                widget.layout.height = "auto"

        def set_states_hidden(widgets):
            for widget in widgets:
                widget.layout.visibility = "hidden"
                # widget.layout.height = '1px'

        if change["new"] in ["Stratified Shuffle Split"]:
            set_states_visible(
                [self._w_validation_size, self._info_validation_method_size]
            )
        else:
            set_states_hidden(
                [self._w_validation_size, self._info_validation_method_size]
            )

        if change["new"] in ["Stratified Metadata k-fold", "Metadata k-fold"]:
            set_states_visible(
                [self._info_validation_metadata, self._w_validation_metadata]
            )
        else:
            set_states_hidden(
                [self._info_validation_metadata, self._w_validation_metadata]
            )

        if change["new"] in [
            "Stratified K-Fold Cross-Validation",
            "Stratified Shuffle Split",
            "Metadata k-fold",
            "Stratified Metadata k-fold",
        ]:
            set_states_visible(
                [self._w_number_folds, self._info_validation_method_folds]
            )
        else:
            set_states_hidden(
                [self._w_number_folds, self._info_validation_method_folds]
            )

    def _on_segmenter_change(self, change):
        if change["new"] == "Windowing":
            self._w_window_size.disabled = False
            self._w_window_size.layout.visibility = "visible"
            self._info_window_size.layout.visibility = "visible"
        else:
            self._w_window_size.disabled = True
            self._w_window_size.layout.visibility = "hidden"
            self._info_window_size.layout.visibility = "hidden"

    def _refresh(self, b=None):
        if self._dsk:
            self._w_query.options = self._get_query_list()
            self._w_query.values = self._w_query.options[0]
            self._w_seed.options = sorted(self._dsk.seeds.seed_dict.keys())

            if self._dsk.pipeline:
                self._w_pipeline_label.value = (
                    "Pipeline Name: <b>" + self._dsk.pipeline.name + "</b>"
                )
                self.results, self.summary = self._dsk.pipeline.get_results(
                    renderer=self.renderer
                )
                self._set_auto_sense_results()
                self.custom_feature_generator._dsk = self._dsk
                self.custom_feature_generator._refresh()

    def _clear(self):
        self._w_query.options = [""]
        self._w_query.value = ""
        self._w_validation_metadata.options = []

    def create_widget(self):

        info_layout = Layout(width="35px", visibility="visible")

        description_style = {"description_width": "112px"}

        self._w_pipeline_label = HTML(value="Pipeline Name:")
        self._w_place_holder = Label(value="")

        self._w_query = Dropdown(
            description="Query", options=[], style=description_style
        )

        self._w_segment = widgets.Dropdown(
            description="Segmenter",
            options=["", "Query Segmenter", "Windowing"],
            style=description_style,
        )

        self._w_window_size = widgets.BoundedIntText(
            value=1024,
            min=25,
            max=8192,
            step=100,
            description="Window Size:",
            disabled=True,
            style=description_style,
        )

        self._info_segmenter = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Defines type of segmenter to use in your pipeline.",
            layout=info_layout,
        )

        tooltip_text = """
                    Accuracy : Ability to differentiate events correctly. 
                    Accuracy as an good evaluation metrics if the class labels are uniformly distributed.
                    For more detail, see https://en.wikipedia.org/wiki/Accuracy_and_precision
                    
                    f1 score : Helps to measure sensitivity and ability to predict individual events correctly out of all the positive prediction at the same time. 
                    f1 Score might be a better statistical metric to use if there is an uneven class distribution. It seeks a balance between sensitivity and positive prediction.
                    For more detail, see https://en.wikipedia.org/wiki/F1_score            

                    Sensitivity : Ability to predict individual events correctly out of all the positive events.
                    With imbalanced classes, accuracy can give you false assumptions regarding the classifier’s performance.
                    Therefore, using sensitivity is suggested for data sets with imbalanced classes.  
                    For more detail, see https://en.wikipedia.org/wiki/Sensitivity_and_specificity
            """.replace(
            "  ", ""
        )

        self._info_optimization_metric = widgets.Button(
            icon="question", disabled=True, tooltip=tooltip_text, layout=info_layout
        )

        self._info_classifiers_sram = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Defines the maximum SRAM usage of the classifier parameters for the model.",
            layout=info_layout,
        )

        self._info_validation_method = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Select the validation method that will be used to calculate the performance metrics such as accuracy and sensitivity of the model.",
            layout=info_layout,
        )

        self._info_validation_method_size = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Select the percentage of data to hold out in the validation folds.",
            layout=Layout(width="35px"),
        )

        self._info_validation_method_folds = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Select the number of folds for validation .",
            layout=Layout(width="35px"),
        )

        self._info_validation_metadata = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Select the metadata to group by.",
            layout=Layout(width="35px"),
        )

        self._info_balanced_data = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Balance the number of examples from each class by undersampling the majority classes. This will reduce number of examples of each class to match the class with the smallest number of examples in your data set.",
            layout=info_layout,
        )

        self._info_allow_unk = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Uses classifiers which will return unknown when the class falls outside of the known predictive space.",
            layout=info_layout,
        )

        self._info_hierarchical_model = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Optimize the prediction results by creating Hierarchical Binary Models.",
            layout=info_layout,
        )

        self._info_population = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Defines how large the inital population is. A higher population means a larger initial search space is.\nA higher population typically produces better results but takes more time.",
            layout=info_layout,
        )

        self._info_iterations = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Defines the number of iterations the model will go through.\n At each iteration a new population of models is created by mutating the previous iterations population.\nA higher number of iteration produces better results but takes more time.",
            layout=info_layout,
        )

        self._info_recreation_rate = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Rate at which new populations are created during each iteration",
            layout=info_layout,
        )

        self._info_survivor_rate = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Rate at which populations survive through each iteration",
            layout=info_layout,
        )

        self._info_mutation_rate = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Rate at which populations mutate through each iteration",
            layout=info_layout,
        )

        self._info_strip_mean = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Remove the mean from  each data source before before extracting features. This helps avoid overfitting models to noise and drift.",
            layout=info_layout,
        )

        self._info_outlier_filter = widgets.Button(
            icon="question",
            disabled=True,
            tooltip="Filter oultiers for each class using Isolation forest filtering. Filters 5pct. of oultiers",
            layout=info_layout,
        )

        tooltip_window_size = """
            The number of samples to buffer for each event before extracting features and
            performing classification. The window size can have a large effect on model 
            accuracy as well as the size of the resulting knowledge pack. A larger window 
            size will allow your model to capture longer trends at the expense of shorter
            range information. A larger model will also need to store more data for 
            processing which will increase the SRAM as well as the latency.""".replace(
            "  ", ""
        )

        self._info_window_size = widgets.Button(
            icon="question",
            disabled=True,
            tooltip=tooltip_window_size,
            layout=Layout(width="35px"),
        )

        self._w_seed = widgets.Dropdown(
            description="Feature Family", options=[], style=description_style
        )

        self._w_seed_desc = widgets.HTML(
            description="Description", disable=True, style=description_style
        )

        self._w_intereact = widgets.interactive(self._select_seed, Name=self._w_seed)

        self._w_classifiers_sram = widgets.BoundedIntText(
            description="Classifier Size (B)",
            value=32000,
            min=0,
            max=512000,
            style=description_style,
        )

        self._w_iterations = widgets.IntSlider(
            description="Iterations",
            value=4,
            min=1,
            max=15,
            step=1,
            style=description_style,
        )

        self._w_population_size = widgets.IntSlider(
            description="Initial Population",
            value=100,
            min=25,
            max=200,
            step=1,
            style=description_style,
        )

        self._c_reset = Checkbox(description="Reset", value=True)

        self._c_allow_unk = Checkbox(description="Allow Unknown", value=False)

        self._c_hierarchical_model = Checkbox(
            description="Hierarchical Model Optimization", value=False
        )

        self._c_balanced_data = Checkbox(description="Balance Data", value=False)

        self._c_strip_mean = Checkbox(description="Strip Mean", value=False)

        self._c_outlier_filter = Checkbox(description="Filter Outliers", value=False)

        self._w_combine_labels = widgets.Text(description="Combine Labels", value="")

        self._w_validation_method = widgets.Dropdown(
            description="Validation",
            options=[
                "Stratified K-Fold Cross-Validation",
                "Stratified Shuffle Split",
                "Metadata k-fold",
                "Stratified Metadata k-fold",
                "Recall",
            ],
            style=description_style,
        )

        self._w_validation_size = widgets.IntSlider(
            description="Validation(%)",
            value=20,
            min=0,
            max=100,
            step=10,
            style=description_style,
        )

        self._w_validation_size = widgets.IntSlider(
            description="Validation(%)",
            value=20,
            min=0,
            max=100,
            step=10,
            style=description_style,
        )

        self._w_validation_metadata = widgets.Dropdown(
            description="metadata", options=[], style=description_style
        )

        self._w_number_folds = widgets.IntSlider(
            description="# Folds",
            value=5,
            min=2,
            max=10,
            step=1,
            style=description_style,
        )

        self._w_mutation_rate = widgets.FloatSlider(
            description="Mutation Rate",
            value=0.1,
            min=0,
            max=1,
            step=0.05,
            style=description_style,
        )

        self._w_recreation_rate = widgets.FloatSlider(
            description="Recreation Rate",
            value=0.2,
            min=0,
            max=1,
            step=0.05,
            style=description_style,
        )

        self._w_survivor_rate = widgets.FloatSlider(
            description="Survivor Rate",
            value=0.5,
            min=0,
            max=1,
            step=0.05,
            style=description_style,
        )

        self._w_optimization_metric = widgets.Dropdown(
            description="Optimization Metric",
            options=["Accuracy", "f1-score", "Sensitivity"],
            style=description_style,
        )

        self._w_results = qgrid.show_grid(
            DataFrame(
                [[0, 0, 0, 0, 0] for _ in range(5)], columns=autosense_metric_column
            ),
            grid_options={
                "rowHeight": 48,
                "maxVisibleRows": 6,
                "minVisibleRows": 6,
                "editable": False,
                "defaultColumnWidth": 50,
                "forceFitColumns": True,
                "sortable": True,
                "filterable": False,
            },
        )

        self._w_results.layout.width = "95%"
        self._w_results.layout.align_self = "flex-end"

        # , layout=Layout( width='98%', align_self='flex-end'))
        self._b_run = Button(
            icon="play",
            description="Optimize",
            layout=Layout(align_self="center", width="250px"),
        )
        self._b_stop = Button(
            icon="stop",
            description="Stop",
            layout=Layout(align_self="center", width="250px"),
        )
        self._b_refresh = Button(
            icon="refresh", layout=Layout(width="35px", align_self="flex-end")
        )
        self._b_terminate = Button(
            icon="stop",
            description="Terminate",
            layout=Layout(width="25%", align_self="flex-end"),
        )
        self._b_iterate = Button(
            icon="redo",
            description="Iterate",
            layout=Layout(width="98%", align_self="flex-end"),
        )

        self._widget_render_space = HTML()

        self.renderer = WidgetAttributeRenderer(self._widget_render_space, "value")

        self._w_query.observe(self._on_value_change, names="value")
        self._b_run.on_click(self._on_button_clicked)
        self._b_stop.on_click(self._on_stop_button_clicked)
        self._b_refresh.on_click(self._refresh)
        self._b_run.style.button_color = "#90EE90"
        self._b_terminate.on_click(self._terminate_run)
        self._w_validation_method.observe(
            self._on_validation_method_change, names="value"
        )
        self._w_segment.observe(self._on_segmenter_change, names="value")

        self._w_window_size.layout.visibility = "hidden"
        self._info_window_size.layout.visibility = "hidden"
        self._w_validation_size.layout.visibility = "hidden"
        self._info_validation_method_size.layout.visibility = "hidden"
        self._info_validation_metadata.layout.visibility = "hidden"
        self._w_validation_metadata.layout.visibility = "hidden"

        self._refresh()
        self.custom_feature_generator = FeatureGeneratorWidget(None)
        self.custom_feature_generator.create_widget()
        self.custom_feature_generator.hide()

        autosense_tabs = Tab(
            [
                HBox(
                    [
                        VBox(
                            [
                                self._w_pipeline_label,
                                widgets.HTML("<b>Settings</b>"),
                                HBox([self._w_query, self._b_refresh]),
                                HBox([self._w_segment, self._info_segmenter]),
                                HBox([self._w_window_size, self._info_window_size]),
                                widgets.HTML("<b>Target Constraints</b>"),
                                HBox(
                                    [
                                        self._w_optimization_metric,
                                        self._info_optimization_metric,
                                    ]
                                ),
                                HBox(
                                    [
                                        self._w_classifiers_sram,
                                        self._info_classifiers_sram,
                                    ]
                                ),
                                self._w_place_holder,
                                HBox([self._b_run, self._b_stop]),
                            ],
                            layout=Layout(width="800px"),
                        ),
                        VBox(
                            [
                                self._w_place_holder,
                                self._w_results,
                                self._widget_render_space,
                            ]
                        ),
                    ],
                    layout=Layout(
                        width="100%",
                        display="flex",
                        flex_flow="row",
                        justify_content="space-between",
                    ),
                ),
                VBox(
                    [
                        widgets.HTML("<b>Pipeline Settings</b>"),
                        HBox(
                            [self._c_strip_mean, self._info_strip_mean],
                            layout=Layout(align_self="flex-start"),
                        ),
                        HBox(
                            [self._c_balanced_data, self._info_balanced_data],
                            layout=Layout(align_self="flex-start"),
                        ),
                        #HBox(
                        #    [self._c_hierarchical_model, self._info_hierarchical_model],
                        #    layout=Layout(align_self="flex-start"),
                        #),
                        HBox(
                            [self._c_outlier_filter, self._info_outlier_filter],
                            layout=Layout(align_self="flex-start"),
                        ),
                        HBox(
                            [self._c_allow_unk, self._info_allow_unk],
                            layout=Layout(align_self="flex-start"),
                        ),
                        # HBox([self._w_combine_labels],
                        #     layout=Layout(align_self='flex-start')),
                        widgets.HTML("<b>Feature Extractors</b>"),
                        self._w_intereact,
                        self._w_seed_desc,
                        self.custom_feature_generator._w_grid,
                        widgets.HTML("<b>Validation Settings</b>"),
                        HBox(
                            [self._w_validation_method, self._info_validation_method],
                            layout=Layout(align_self="flex-start"),
                        ),
                        HBox(
                            [self._w_number_folds, self._info_validation_method_folds],
                            layout=Layout(align_self="flex-start"),
                        ),
                        HBox(
                            [
                                self._w_validation_size,
                                self._info_validation_method_size,
                            ],
                            layout=Layout(align_self="flex-start"),
                        ),
                        HBox(
                            [
                                self._w_validation_metadata,
                                self._info_validation_metadata,
                            ],
                            layout=Layout(align_self="flex-start"),
                        ),
                    ]
                ),
                VBox(
                    [
                        widgets.HTML("<b>Genetic Search Setttings</b>"),
                        HBox(
                            [self._w_population_size, self._info_population],
                            layout=Layout(align_self="flex-start"),
                        ),
                        HBox(
                            [self._w_iterations, self._info_iterations],
                            layout=Layout(align_self="flex-start"),
                        ),
                        HBox(
                            [self._w_recreation_rate, self._info_recreation_rate],
                            layout=Layout(align_self="flex-start"),
                        ),
                        HBox(
                            [self._w_mutation_rate, self._info_mutation_rate],
                            layout=Layout(align_self="flex-start"),
                        ),
                        HBox(
                            [self._w_survivor_rate, self._info_survivor_rate],
                            layout=Layout(align_self="flex-start"),
                        ),
                    ]
                ),
            ]
        )

        autosense_tabs.set_title(0, "Main Settings")
        autosense_tabs.set_title(1, "Pipeline Settings")
        autosense_tabs.set_title(2, "Advanced Settings")

        self._widget = VBox([autosense_tabs])

        return self._widget
