from ipywidgets import HBox, VBox, Dropdown, Button, Image, Layout, Accordion
from numpy import mean, sort
from bqplot.marks import Graph, Image
from bqplot.scales import LinearScale, OrdinalScale
from bqplot.figure import Figure
from bqplot import Tooltip, ColorScale
from bqplot.axes import Axis


class HierarchicalModelVisualizationWidget:
    """
    Visualize hierarchical model tree.
    """

    def __init__(self, dsk=None, kp=None):
        self._dsk = dsk
        self.kp = kp
        self.plot_tree(kp)

    def find_deep(self, model_name):
        if model_name == "Parent":
            model_index = 0
        else:
            model_index = int(model_name.split("_")[1])

        height_of_tree = {
            "600": [0],
            "500": range(2, 4),
            "400": range(4, 8),
            "300": range(8, 16),
            "200": range(16, 32),
            "100": range(32, 64),
            "1": range(64, 128),
        }

        return int([h for h, v in height_of_tree.items() if model_index in v][0])

    def compute_x_axis(self, y_axis_loc, link_data):
        x_axis_location = {0: 3}
        distance = 0.64
        previous_source = y_axis_loc[0]
        x_axis_loc = [3]

        for i in link_data:
            target = i["target"]
            source = i["source"]

            if y_axis_loc[target] != previous_source:
                distance = distance * 0.5

            if (i["target"] % 2) == 0:
                x_axis_location[target] = x_axis_location[source] + distance
            else:
                x_axis_location[target] = x_axis_location[source] - distance

            x_axis_loc.append(x_axis_location[target])
            previous_source = y_axis_loc[target]

        return x_axis_loc

    def score_nodes(self, acc_dict, kb_description):
        label_list = list(acc_dict.keys() - kb_description.keys())
        while [label for label, value in acc_dict.items() if value is None]:

            for node in [label for label, value in acc_dict.items() if value is None]:
                both_node = (
                    sum(
                        [
                            label in kb_description.keys()
                            for _, label in kb_description[node]["results"].items()
                        ]
                    )
                    == 2
                )
                corrected_score = [
                    acc_dict[label]
                    for _, label in kb_description[node]["results"].items()
                ]

                # this is a node has 2 child nodes with corrected stat
                if both_node and None not in corrected_score:
                    acc_dict[node] = mean(
                        [
                            acc_dict[label]
                            for _, label in kb_description[node]["results"].items()
                        ]
                    )

                # this is a node has 1 child node and one leaf with corrected stat
                if (
                    sum(
                        [
                            label in label_list
                            for _, label in kb_description[node]["results"].items()
                        ]
                    )
                    == 1
                ):
                    acc_list = []
                    for _, label in kb_description[node]["results"].items():
                        if label in kb_description.keys():
                            acc_list.append(acc_dict[label])
                        else:
                            acc_list.append(acc_dict[label]["Accuracy"])

                    acc_dict[node] = mean(acc_list)

        return acc_dict

    def compute_hm_graph_paramenter(self, kp):
        kb_description = kp.knowledgepack_description
        kb_description_list = list(kb_description.keys())

        link_data = []
        colors = []
        node_names = []
        y_axis_loc = []
        num = 1
        link_map = {"Parent": 0}
        acc_dict = {}

        for i, node in enumerate(kb_description_list):
            node_height = self.find_deep(node)
            y_axis_loc.append(node_height)
            uuid = kb_description[node]["uuid"]
            temp_kp = self._dsk.get_knowledgepack(uuid)
            class_map = temp_kp.class_map
            acc_dict[node] = None

            if node == "Parent":
                hm_confusionmatrix = temp_kp.model_results["metrics"]["hierarchical"][
                    "ConfusionMatrix"
                ]

            child_nodes = kb_description[node]["results"]
            if node not in node_names:
                node_names.append(node)
                colors.append("#1f77b4")

            min_dec = 1
            leaf_acc_list = []
            for cn_index, cn_node in child_nodes.items():
                if cn_node != "Report":
                    if cn_node not in node_names:
                        node_names.append(cn_node)
                        colors.append("#1f77b4")
                        link_map[cn_node] = num
                else:
                    colors.append("#d62728")
                    y_axis_loc.append(node_height - 100)
                    class_label = class_map[cn_index]
                    class_acc = round(
                        100
                        * hm_confusionmatrix[class_label][class_label]
                        / sum(list(hm_confusionmatrix[class_label].values())),
                        2,
                    )
                    leaf_acc_list.append(class_acc)
                    acc_dict[class_label] = {
                        "Accuracy": class_acc,
                        "Predictions": hm_confusionmatrix[class_label],
                    }
                    kb_description[node]["results"][cn_index] = class_label
                    node_names.append(class_label)

                # This one compute acc scores for nodes that has 2 leafs
                if len(leaf_acc_list) == 2:
                    acc_dict[node] = mean(leaf_acc_list)

                link_data.append({"source": link_map[node], "target": num, "value": 1})
                num = num + 1

        y_axis_loc = list(sort(y_axis_loc)[::-1])
        shape_attrs = {"rx": 10, "ry": 10, "width": 60}
        node_data = []
        acc_dict = self.score_nodes(acc_dict, kb_description)

        for node_name in node_names:
            node_data_dict = {
                "label": node_name,
                "shape": "rect",
                "shape_attrs": shape_attrs,
                "Model": node_name,
                "Accuracy": str(acc_dict[node_name]),
            }
            node_data.append(node_data_dict)

        x_axis_loc = self.compute_x_axis(y_axis_loc, link_data)
        # compute the average accuracy of all leafs
        class_labels = list(acc_dict - kp.knowledgepack_description.keys())
        over_all_accuracy = round(
            mean([acc_dict[node]["Accuracy"] for node in class_labels]), 2
        )

        return (
            node_names,
            link_data,
            node_data,
            y_axis_loc,
            x_axis_loc,
            colors,
            over_all_accuracy,
        )

    def plot_tree(self, kp):
        node_names, link_data, node_data, y_axis_loc, x_axis_loc, colors, over_all_accuracy = self.compute_hm_graph_paramenter(
            kp
        )
        fig_layout = Layout(width="1024px", height="500px")
        graph = Graph(
            node_data=node_data,
            link_data=link_data,
            link_type="line",
            colors=colors,
            directed=False,
            scales={
                "x": LinearScale(),
                "y": LinearScale(),
                "link_color": ColorScale(scheme="Greens"),
            },
            x=x_axis_loc,
            y=y_axis_loc,
        )

        tooltip = Tooltip(fields=["Model", "Accuracy"], formats=["", ""])
        graph.tooltip = tooltip

        display(
            Figure(
                marks=[graph],
                layout=fig_layout,
                title="Hierarchical Model Tree Accuracy: " + str(over_all_accuracy),
            )
        )

