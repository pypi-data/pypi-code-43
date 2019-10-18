# Copyright 2019 Cognite AS

import os
from typing import *

from google.protobuf.struct_pb2 import Struct

from cognite.seismic._api.api import API

if not os.getenv("READ_THE_DOCS"):

    from cognite.seismic.protos.ingest_service_messages_pb2 import (
        DeleteFileRequest,
        EditFileRequest,
        IngestFileRequest,
        RegisterFileRequest,
    )
    from cognite.seismic.protos.query_service_messages_pb2 import (
        FileCoverageRequest,
        FileLineQueryRequest,
        FileQueryRequest,
        HeaderFileQueryRequest,
        LineBasedRectangle,
        PositionQuery,
        SegYQueryRequest,
    )
    from cognite.seismic.protos.types_pb2 import CRS, FileStep, GeoJson, Geometry, Wkt


class FileAPI(API):
    def __init__(self, query, ingestion, metadata):
        super().__init__(metadata=metadata, query=query, ingestion=ingestion)

    def get(self, id: Optional[str] = None, name: Optional[str] = None):
        """Get a file by either id or name.

        Args:
            id (str): Id of the file.
            name (str): Name of the file.

        Returns:
            GetFileResponse: File information including file id and name, crs, path, survey_name and the last step of
             the ingestion job

        """
        file = self.identify(id, name)
        request = FileQueryRequest(file=file)
        return self.query.GetFile(request, metadata=self.metadata)

    def get_binary_header(self, id: Optional[str] = None, name: Optional[str] = None, include_raw_header=False):
        """Get binary header of a file by either its id or name

        Args:
            id (str): Id of the file.
            name (str): Name of the file.
            include_raw_header (bool): True of raw header should be included.

        Returns:
            GetBinaryHeaderResponse: binary header
        """
        file = self.identify(id, name)
        request = HeaderFileQueryRequest(file=file, include_raw_header=include_raw_header)
        return self.query.GetBinaryHeader(request, metadata=self.metadata)

    def get_text_header(self, id: Optional[str] = None, name: Optional[str] = None, include_raw_header=False):
        """Get text header of a file by either its id or name.

        Args:
            id (str): Id of the file.
            name (str): Name of the file.
            include_raw_header (bool): True of the raw header should be included.

        Returns:
            GetTextHeaderResponse: text header
        """
        file = self.identify(id, name)
        request = HeaderFileQueryRequest(file=file, include_raw_header=include_raw_header)
        return self.query.GetTextHeader(request, metadata=self.metadata)

    def get_file_coverage(
        self, id: Optional[str] = None, name: Optional[str] = None, crs: str = "EPSG:23031", in_wkt: bool = False
    ):
        """Get the coverage polygon for a given file identified by either its id or name

        Args:
            id (str): Id of the file.
            name (str): Name of the file.
            crs (str): (Optional) converts coverage to given CRS if provided. Else returns the original.
            in_wkt (bool): True to return WKT, False (default) to return geoJson.

        Returns:
            DataCoverageResponse: coverage polygon.
        """
        file = self.identify(id, name)
        request = FileCoverageRequest(file=file, crs={"crs": crs}, in_wkt=in_wkt)
        return self.query.GetFileDataCoverage(request, metadata=self.metadata)

    @staticmethod
    def _verify_input(crs: str = None, wkt: str = None, geo_json: str = None):
        if not crs:
            raise Exception("CRS is required")
        if not wkt and not geo_json:
            raise Exception("Either `wkt` or `geo_json` needs to be specified")
        if wkt and geo_json:
            raise Exception("Only `wkt` or `geo_json` should be specified")

    def get_segy(self, id: Optional[str] = None, name: Optional[str] = None):
        """Get a full SEGY file by either its id or name

        Args:
            id (str): Id of the file.
            name (str): Name of the file.

        Returns:
            SegYQueryResponse: SEGY file
        """
        file = self.identify(id, name)
        request = SegYQueryRequest(file=file)
        return [i for i in self.query.GetSegYFile(request, metadata=self.metadata)]

    def get_segy_by_lines(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        top_left_inline: int = None,
        top_left_crossline: int = None,
        bottom_right_inline: int = None,
        bottom_right_crossline: int = None,
    ):
        """Get a part of a SEGY file with data inside a given range of inlines and crosslines

        Args:
            id (str): Id of the file.
            name (str): Name of the file.
            top_left_inline (int): Top left inline index.
            top_left_crossline (int): Top left crossline index.
            bottom_right_inline (int): Bottom right inline index.
            bottom_right_crossline (int): Bottom right crossline index.

        Returns:
            SegYQueryResponse: SEGY file

        """
        file = self.identify(id, name)
        top_left = PositionQuery(iline=top_left_inline, xline=top_left_crossline)
        bottom_right = PositionQuery(iline=bottom_right_inline, xline=bottom_right_crossline)
        rectangle = LineBasedRectangle(top_left=top_left, bottom_right=bottom_right)
        request = SegYQueryRequest(file=file, lines=rectangle)
        return [i for i in self.query.GetSegYFile(request, metadata=self.metadata)]

    def get_segy_by_geometry(
        self, id: Optional[str] = None, name: Optional[str] = None, crs: str = None, wkt: str = None, geo_json=None
    ):
        """Get a part of a SEGY file with data inside an arbitrary 2D polygon

        Args:
            id (str): Id of the file.
            name (str): Name of the file.
            crs (str): CRS
            wkt (str): polygon in WKT format
            geo_json (dict): polygon in geoJson format

        Returns:

        """
        file = self.identify(id, name)
        self._verify_input(crs, wkt, geo_json)
        if geo_json:
            geo_json_struct = Struct()
            geo_json_struct.update(geo_json)
            geo = Geometry(crs=CRS(crs=crs), geo=GeoJson(json=geo_json_struct))
        else:
            geo = Geometry(crs=CRS(crs=crs), wkt=Wkt(geometry=wkt))

        request = SegYQueryRequest(file=file, polygon=geo)
        return [i for i in self.query.GetSegYFile(request, metadata=self.metadata)]

    def get_line_range(self, id: Optional[str] = None, name: Optional[str] = None):
        """Get the minimum and maximum crosslines and inlines

        Args:
            id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            name (str, optional): File can be specified either by name or id (id will be used first if both are provided)

        Returns:
            The line range
        """
        file = self.identify(id, name)
        request = FileQueryRequest(file=file)
        return self.query.GetFileLineRange(request, metadata=self.metadata)

    def get_crossline_by_inline(self, id: Optional[str] = None, name: Optional[str] = None, inline: int = None):
        """Get the range of crosslines by a specific inline

        Args:
            id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            inline (int): The inline for which to get a crossline

        Returns:
            The line range
        """
        file = self.identify(id, name)
        request = FileLineQueryRequest(file=file, line=inline)
        return self.query.GetCrosslinesByInline(request, metadata=self.metadata)

    def get_inline_by_crossline(self, id: Optional[str] = None, name: Optional[str] = None, crossline: int = None):
        """Get the range of inlines by a specific crossline

        Args:
            id (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            name (str, optional): File can be specified either by name or id (id will be used first if both are provided)
            crossline (int): The crossline for which to get an inline

        Returns:
            The line range
        """
        file = self.identify(id, name)
        request = FileLineQueryRequest(file=file, line=crossline)
        return self.query.GetInlinesByCrossline(request, metadata=self.metadata)

    def register(
        self,
        survey_id: Optional[str] = None,
        survey_name: Optional[str] = None,
        bucket: str = None,
        name: str = None,
        crs: str = None,
        metadata: dict = None,
    ):
        """Register a file on a survey

        Args:
            survey_id (str): The survey is identified by either the id or the name. If both are given, the id is used.
            survey_name (str): The survey is identified by either the id or the name. If both are given, the id is used.
            bucket (str): Path to the directory in Google Cloud Storage in which the file is stored
            name (str): The file name in Google Cloud Storage. Also used for identifying the file
            crs (str): The CRS of the file
            metadata (dict, optional): A string -> string dictionary with any metadata to add about the file

        Returns:
             The response from the gRPC server with the id the file was registered on.
        """
        survey = self.identify(survey_id, survey_name)
        request = RegisterFileRequest(survey=survey, path=bucket, name=name, crs=CRS(crs=crs), metadata=metadata)
        return self.ingestion.RegisterFile(request, metadata=self.metadata)

    def ingest(self, id: Optional[str] = None, name: Optional[str] = None, start_step: int = 1):
        """Ingest a registered file.

        Args:
            id(str): File id of the registered file.
            name(str): File name of the registered file.
            start_step(int): Selected step to start ingestion. Leave blank to start from last completed step.
               0: REGISTER

               1: INSERT_FILE_HEADERS

               2: INSERT_TRACE_HEADERS

               3: INSERT_DATA

               4: COMPUTE_COVERAGE

               5: COMPUTE_GRID
        Returns:
            IngestFileResponse: a Job id that can be used to query for status of the ingestion job, and the file id.
        """
        if start_step not in FileStep.values():
            raise Exception("Invalid `start_step`")
        file = self.identify(id, name)
        if not start_step:
            request = IngestFileRequest(file=file)
        else:
            request = IngestFileRequest(file=file, start_step=start_step)
        return self.ingestion.IngestFile(request, metadata=self.metadata)

    def delete(self, id: Optional[str] = None, name: Optional[str] = None, keep_registered: bool = None):
        """Delete a file by either its id or name

        Args:
            id: Id of the file.
            name: Name of the file.
            keep_registered: True if the file should be kept registered.

        Returns:
            Nothing
        """
        file = self.identify(id, name)
        request = DeleteFileRequest(file=file, keep_registered=keep_registered)
        return self.ingestion.DeleteFile(request, metadata=self.metadata)

    def edit(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        bucket: str = None,
        new_name: str = None,
        metadata: dict = None,
        crs: str = None,
    ):
        """Edit a file by either its id or name.

        Args:
            id (str): Id of the file.
            name (str): Name of the file.
            bucket (str): New path of the file.
            new_name (str): New name of the file.
            metadata (dict): New metadata of the file.
            crs (str): New CRS of the file.

        Returns:
            EditFileResponse: File information including file id, name, path and crs.
        """
        file = self.identify(id, name)
        request = EditFileRequest(file=file, path=bucket, name=new_name, metadata=metadata, crs=CRS(crs=crs))
        return self.ingestion.EditFile(request=request, metadata=self.metadata)
