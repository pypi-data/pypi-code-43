import sys
from typing import Dict, Optional, Union, List
from uuid import UUID

import pandas as pd

from datalogue.errors import DtlError
from datalogue.models.graph import Graph, Node, NodeDef, Path
from datalogue.utils import _parse_string_list


class SchemaNode(Node):
    """
    Describes schema node
    """

    def __init__(self, id: UUID, label: str, dataType: str, ontologyNodeId: Optional[UUID],
                 ontologyNodePath: Optional[List[str]]):
        """
        Builds SchemaNode object

        :param id: schema node id
        :param label: column name
        :param dataType: type of the data
        :param ontologyNodeId: user-classified ontology id for this node
        :param ontologyNodePath: user-classified ontology path for this node
        """

        self.id = id
        self.label = label
        self.dataType = dataType
        self.ontologyNodeId = ontologyNodeId
        self.ontologyNodePath = ontologyNodePath
        Node.__init__(self, id, label)

    @staticmethod
    def _as_payload(self) -> Union[DtlError, dict]:
        """
        Dictionary representation of the object with camelCase keys
        :return:
        """

        return {
            "id": self.id,
            "label": self.label,
            "dataType": self.dataType
        }

    def _schema_node_from_payload(json: dict) -> Union[DtlError, 'SchemaNode']:
        node_id = json.get("id")
        if node_id is None:
            return DtlError("SchemaNode has to have a 'id' key")

        label = json.get("label")
        if label is None:
            return DtlError("SchemaNode has to have a 'label' key")

        dataType = json.get("dataType")
        userOntologies = json.get("userOntologies")
        ontology_node_id = None
        ontology_node_path = None
        if userOntologies is not None and isinstance(userOntologies, dict):
            ontology_node_id = userOntologies.get("ontologyNodeId")
            ontology_node_path = _parse_string_list(userOntologies.get("ontologyNodePath"))

        return SchemaNode(node_id, label, dataType, ontology_node_id, ontology_node_path)




class GraphSampleNode(Node):
    """
    Describes schema node
    """

    def __init__(self, id: UUID, label: str, value: str):
        """
        Builds SchemaNode object

        :param id: schema node id
        :param label: column name
        :param value: value of the data
        """

        self.id = id
        self.label = label
        self.value = value
        Node.__init__(self, id, label)

    def _sample_node_from_payload(json: dict) -> Union[DtlError, 'GraphSampleNode']:
        node_id = json.get("id")
        if node_id is None:
            return DtlError("SampleNode has to have a 'id' key")

        label = json.get("label")
        if label is None:
            return DtlError("SampleNode has to have a 'label' key")

        value = json.get("value")
        if "value" not in json:
            return DtlError("SampleNode has to have a 'value' key")

        return GraphSampleNode(str(node_id), label, value)



class AbstractDataGraph(Graph):
    node_decoder = GraphSampleNode._sample_node_from_payload


class AbstractDataSchema(Graph):
    node_decoder = SchemaNode._schema_node_from_payload



class SchemaOntologyRow:
    """
    Represents printable representation of schema, its associated ontology & samples data.
    """

    def __init__(self, schema_node_def: NodeDef, samples: List[AbstractDataGraph]):
        self.schema_node_def = schema_node_def
        self.samples = samples

    def to_array(self, is_full_path: bool):
        def get_sample_val(index: int, full_path: Path):
            if len(self.samples) > index:
                sample = self.samples[index]
                return sample.path_to_node[full_path].node.value
            else:
                return None

        schema_node = self.schema_node_def.node
        full_path = self.schema_node_def.full_path
        sample_1_val = get_sample_val(0, full_path)
        sample_2_val = get_sample_val(1, full_path)
        sample_3_val = get_sample_val(2, full_path)
        ontology_node_id = schema_node.ontologyNodeId
        if ontology_node_id is None:
            ontology_node_id = "\"\""
        if not is_full_path:
            if schema_node.ontologyNodePath is not None and len(schema_node.ontologyNodePath) > 0:
                ontology_node_label = schema_node.ontologyNodePath[-1]
            else:
                ontology_node_label = "\"\""
            return [schema_node.id, schema_node.label, schema_node.dataType,
                    ontology_node_label, ontology_node_id, sample_1_val, sample_2_val,
                    sample_3_val]
        else:
            if schema_node.ontologyNodePath is not None:
                ontology_node_label = schema_node.ontologyNodePath
            else:
                ontology_node_label = ["\"\"", "\"\""]
            return [schema_node.id, self.schema_node_def.full_path, schema_node.dataType,
                    ontology_node_label, ontology_node_id, sample_1_val, sample_2_val,
                    sample_3_val]


class Schema:
    """
    Represents a schema.
    """

    def __init__(self, data_schema: AbstractDataSchema, samples: Optional[List[AbstractDataGraph]]):
        """
        Represents a schema structure

        :param data_schema: Represents data schema
        :param samples: A collection of samples data with the same structure as data_schema
        """

        self.data_schema = data_schema
        self.samples = samples

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'Schema']:
        schema = json.get("schema")
        samples_json = json.get("samples")
        if schema is None:
            return DtlError("Schema has to have a 'schema' key")
        if samples_json is None:
            return DtlError("Schema has to have a 'samples' key")
        ads = AbstractDataSchema._from_payload(schema, AbstractDataSchema.node_decoder)

        if samples_json is None:
            adg = None
        else:
            adg = []
            for obj in samples_json:
                parsed_obj = AbstractDataGraph._from_payload(obj, AbstractDataGraph.node_decoder)

                if isinstance(parsed_obj, DtlError):
                    return parsed_obj
                else:
                    adg.append(parsed_obj)
        return Schema(ads, adg)

    def print(self, full_path: bool):
        pd.set_option('max_colwidth', 29)
        nodes_def = self.data_schema.get_nodes()
        res = []
        if len(nodes_def) > 1000:
            return DtlError("Extremely large schema, please contact Datalogue support to enable larger schemas")
        for node_def in nodes_def:
            res.append(SchemaOntologyRow(node_def, self.samples).to_array(full_path))
        df = pd.DataFrame(pd.np.array(res),
                     columns=['schema_node_id', 'schema_node_name', 'schema_node_type', 'ontology_node_name',
                              'ontology_node_id', 'sample1', 'sample2', 'sample3'])
        sys.stdout.write(df.to_string(index=False))
