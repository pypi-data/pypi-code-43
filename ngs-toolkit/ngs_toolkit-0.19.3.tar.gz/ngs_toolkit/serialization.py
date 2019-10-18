
from ngs_toolkit import Analysis
from marshmallow import Schema, fields, post_load
from marshmallow_dataframe import SplitDataFrameSchema


# python_to_marshmallow = {
#     v: getattr(fields, v.__name__.capitalize())()
#     for v in [int, float, dict]}
# python_to_marshmallow.update({
#     type(None): fields.Inferred(),
#     str: fields.String(),
#     list: fields.List(fields.FieldABC)})
# a = Analysis()
# schema = Schema.from_dict({k: python_to_marshmallow[type(v)] for k, v in a.__dict__.items()})


pep = "/tmp/pytest-of-afr/pytest-current/popen-gw1/test_peak_chromatin_state0/"
pep += "test-project_ATAC-seq_hg38_1_1000_3/metadata/project_config.yaml"
a = Analysis(from_pep=pep)
a.load_data(only_these_keys=['sites', 'matrix_raw'])
a.normalize()


class MatrixRaw(SplitDataFrameSchema):
    """Automatically generated schema for animal dataframe"""
    class Meta:
        dtypes = a.matrix_raw.dtypes


class MatrixNorm(SplitDataFrameSchema):
    """Automatically generated schema for animal dataframe"""
    class Meta:
        dtypes = a.matrix_norm.dtypes


class SampleSchema(Schema):
    sample_name = fields.String()
    name = fields.String()
    # sample-specific attributes
    a = fields.String()
    protocol = fields.String()
    organism = fields.String()
    merged_cols = fields.String()
    derived_cols_done = fields.String()
    sheet_attributes = fields.String()
    required_paths = fields.String()
    yaml_file = fields.String()
    merged = fields.String()
    paths = fields.String()
    genome = fields.String()
    results_subdir = fields.String()
    bigwig = fields.String()
    track_url = fields.String()
    aligned_filtered_bam = fields.String()
    peaks = fields.String()
    summit = fields.String()


class ProjectSchema(Schema):
    dcc = fields.String()
    permissive = fields.String()
    file_checks = fields.String()
    _subproject = fields.String()
    config_file = fields.String()
    # project-specific attributes
    project_name = fields.String()
    project_description = fields.String()
    username = fields.String()
    email = fields.String()
    metadata = fields.String()
    sample_attributes = fields.String()
    group_attributes = fields.String()
    data_sources = fields.String()
    implied_attributes = fields.String()
    compute_packages = fields.String()
    trackhubs = fields.String()
    constant_attributes = fields.String()
    _sections = fields.String()
    name = fields.String()
    derived_attributes = fields.String()
    _main_index_cols = fields.String()
    _subs_index_cols = fields.String()
    _subsample_table = fields.String()
    _sample_table = fields.String()
    _samples = fields.String()
    root_dir = fields.String()


class AnalysisSchema(Schema):
    name = fields.String()
    root_dir = fields.String()

    root_dir = fields.String()
    data_dir = fields.String()
    results_dir = fields.String()

    prj = fields.Nested(ProjectSchema, only=[""])
    samples = fields.Nested(SampleSchema, only=[""])

    data_type = fields.String(allow_none=True)
    __data_type__ = fields.String(allow_none=True)
    var_unit_name = fields.String(allow_none=True)
    quantity = fields.String(allow_none=True)
    norm_units = fields.String(allow_none=True)
    raw_matrix_name = fields.String(allow_none=True)
    norm_matrix_name = fields.String(allow_none=True)
    annot_matrix_name = fields.String(allow_none=True)
    feature_matrix_name = fields.String(allow_none=True)
    norm_method = fields.String(allow_none=True)

    # for some reason only index and columns are being serialized,
    # I guess there should be one more field "data"
    matrix_raw = fields.Nested(MatrixRaw)
    matrix_norm = fields.Nested(MatrixNorm)

    @post_load
    def make_analysis(self, data, **kwargs):
        import inspect
        args = {
            k: v for k, v in data.items()
            if k in inspect.signature(Analysis).parameters.keys()}
        a2 = Analysis(**args)
        attrs = {
            k: v for k, v in data.items()
            if k not in inspect.signature(Analysis).parameters.keys()}
        for k, v in attrs.items():
            setattr(a2, k, v)

        return a2


schema = AnalysisSchema()
analysis_data = schema.dump(a)

a2 = schema.load(analysis_data)

summary_schema = AnalysisSchema(exclude=["prj", "samples"])
a2_summary = summary_schema.load(analysis_data)
