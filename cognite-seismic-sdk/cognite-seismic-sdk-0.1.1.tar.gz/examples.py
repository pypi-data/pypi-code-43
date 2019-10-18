from cognite.seismic import CogniteSeismicClient

# create a client
client = CogniteSeismicClient()

file_id = "some_id"

# surveys
survey = client.survey.get(name="F3")
print(survey)
surveys = client.survey.list()

search_results = client.survey.search(
    crs="EPSG:23031",
    wkt="POLYGON ((469500 6637210, 469500 6637310, 469530 6637310, 469530 6637210, 469500 6637210))",
    include_metadata=True,
)

# register a survey
client.survey.register(name="my_survey", metadata={"first_key": "first_value"})
# edit a survey
client.survey.edit(id="id_survey", name="new_name")

# file
file = client.file.get(id=file_id)

binary_header = client.file.get_binary_header(id=file_id)

coverage = client.file.get_file_coverage(id=file_id)

segy_by_lines = client.file.get_segy_by_lines(
    id=file_id,
    top_left_inline=36825,
    top_left_crossline=137405,
    bottom_right_inline=36827,
    bottom_right_crossline=137409,
)

segy_by_geometry = client.file.get_segy_by_geometry(
    id=file_id,
    crs="EPSG:23031",
    wkt="POLYGON ((469500 6637210, 469500 6637310, 469530 6637310, 469530 6637210, 469500 6637210))",
)

line_range = client.file.get_line_range(id=file_id)

crossline = client.file.get_crossline_by_inline(id=file_id, inline=36825)
inline = client.file.get_inline_by_crossline(id=file_id, crossline=137179)

# ingest a file
client.file.ingest(name="some_name", start_step=1)

# edit and delete files
client.file.edit(id="file2", metadata={"key": "value"})
client.file.delete(id="file4", keep_registered=True)

# jobs
status = client.job.status(job_id="some_id")

# traces
traces_by_line = client.trace.get_trace_by_line(file_id=file_id, inline=37370, crossline=137650)
traces_by_coord = client.trace.get_trace_by_coordinates(file_id=file_id, x=1, y=2)


# slices

crossline = client.slice.get_crossline(crossline=400, file_name="F3.sgy", from_line=400, to_line=405)
inline = client.slice.get_inline(inline=400, file_name="F3.sgy")
crossline.to_array()  # will return a 2D numpy array with the traces in order

arb_line = client.slice.get_arbitrary_line(
    file_name="F3.sgy", x0=605416, y0=608850, x1=610000, y1=6085000, crs="EPSG:23031", interpolation_method=1
)
arb_line.to_array()  # will return a 2D numpy array with the traces in order

# cube
# returns a list of Traces (with inline and crossline)
cube_by_lines = client.volume.get_cube_by_lines(
    file_id=file_id,
    top_left_inline=36825,
    top_left_crossline=137405,
    bottom_right_inline=36827,
    bottom_right_crossline=137409,
)
# transform traces to numpy array
trace_array = cube_by_lines.to_array()

cube_by_geometry = client.volume.get_cube_by_geometry(
    file_id=file_id,
    crs="EPSG:23031",
    wkt="POLYGON ((469500 6637210, 469500 6637310, 469530 6637310, 469530 6637210, 469500 6637210))",
).to_array()


# time slice
time_slice_by_lines = client.time_slice.get_time_slice_by_lines(
    file_id=file_id,
    top_left_inline=36825,
    top_left_crossline=137405,
    bottom_right_inline=36827,
    bottom_right_crossline=137409,
    z=0,
).to_array()

time_slice_by_geometry = client.time_slice.get_time_slice_by_geometry(
    file_id=file_id,
    crs="EPSG:23031",
    wkt="POLYGON ((469500 6637210, 469500 6637310, 469530 6637310, 469530 6637210, 469500 6637210))",
    z=1,
).to_array()
