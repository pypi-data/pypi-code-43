import vcr as _vcr

vcr = _vcr.VCR(
    cassette_library_dir="resources/cassettes",
    path_transformer=_vcr.VCR.ensure_suffix(".yaml"),
    filter_headers=["authorization"],
    record_mode="once",
    match_on=["method", "path", "query"],
)
