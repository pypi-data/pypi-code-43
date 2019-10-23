# coding: utf-8
"""
    assetic.layertools  (layertools.py)
    Tools to assist with using arcgis integration with assetic
"""
from __future__ import absolute_import

import arcpy

try:
    import pythonaddins
except:
    # ArcGIS Pro doesn't have this library
    pass
import assetic
import six
from arcgis2geojson import arcgis2geojson
import json
import io
import csv
from ..config import Config
from .commontools import CommonTools
from .commontools import DummyProgressDialog


class LayerTools(object):
    """
    Class to manage processes that relate to a GIS layer
    """

    def __init__(self, layerconfig=None):

        self.config = Config()
        if layerconfig == None:
            self._layerconfig = self.config.layerconfig
        else:
            self._layerconfig = layerconfig
        self._assetconfig = self._layerconfig.assetconfig
        self.asseticsdk = self.config.asseticsdk

        # initialise common tools so can use messaging method
        self.commontools = CommonTools()
        self.commontools.force_use_arcpy_addmessage = \
            self.config.force_use_arcpy_addmessage
        # instantiate assetic.AssetTools
        self.assettools = assetic.AssetTools(self.asseticsdk.client)

        # get logfile name to help user find it
        self.logfilename = ""
        for h in self.asseticsdk.logger.handlers:
            try:
                self.logfilename = h.baseFilename
            except:
                pass

    def get_layer_config(self, lyr, purpose):
        """
        For the given layer get the config settings. Depending on purpose not
        all config is required, so only get relevant config
        :param lyr: is the layer to process (not layer name but ArcMap layer)
        :param purpose: one of 'create','update','delete','display'
        """
        lyr_config_list = [j for i, j in enumerate(
            self._assetconfig) if j["layer"] == lyr.name]
        if len(lyr_config_list) == 0:
            if purpose not in ["delete"]:
                msg = "No configuration for layer {0}".format(lyr.name)
                self.commontools.new_message(msg)
            return None, None, None
        lyr_config = lyr_config_list[0]

        # create a list of the fields in the layer to compare config with
        actuallayerflds = list()
        for fld in arcpy.Describe(lyr).Fields:
            actuallayerflds.append(str(fld.Name))

        if purpose in ["create", "update"]:
            # from config file build list of arcmap fields to query
            fields = list(six.viewvalues(lyr_config["corefields"]))
            if fields is None:
                msg = "missing 'corefields' configuration for layer {0}".format(
                    lyr.name)
                self.commontools.new_message(msg)
                return None, None, None
            if "attributefields" in lyr_config:
                attfields = list(six.viewvalues(lyr_config["attributefields"]))
                if attfields != None:
                    fields = fields + attfields

            for component in lyr_config["components"]:
                compflds = list(six.viewvalues(component["attributes"]))
                if compflds:
                    fields = fields + compflds
                for dimension in component["dimensions"]:
                    dimflds = list(six.viewvalues(dimension["attributes"]))
                    if dimflds:
                        fields = fields + dimflds
            if "addressfields" in lyr_config:
                addrfields = list(six.viewvalues(lyr_config["addressfields"]))
                if addrfields is not None:
                    fields = fields + addrfields

            # check fields from config are in layer
            if fields is not None:
                # create unique list (may not be unique if components or
                # dimensions config use same field for common elements
                fields = list(set(fields))

                # loop through list and check fields are in layer
                for configfield in fields:
                    if configfield not in actuallayerflds:
                        msg = "Field [{0}] is defined in configuration but is " \
                              "not in layer {1}, check logfile for field list" \
                              "".format(configfield, lyr.name)
                        self.commontools.new_message(msg)
                        self.asseticsdk.logger.warning(msg)
                        msg = "Fields in layer {0} are: {1}".format(lyr.name,
                                                                    actuallayerflds)
                        self.asseticsdk.logger.warning(msg)
                        return None, None, None
            # add these special fields to get geometry and centroid
            fields.append("SHAPE@")
            fields.append("SHAPE@XY")
        else:
            fields = None

        idfield = None
        if purpose in ["delete", "display"]:
            # get the Assetic unique ID column in ArcMap
            assetid = None
            if "id" in lyr_config["corefields"]:
                idfield = lyr_config["corefields"]["id"]
            else:
                if "asset_id" in lyr_config["corefields"]:
                    idfield = lyr_config["corefields"]["asset_id"]
                else:
                    msg = "Asset ID and/or Asset GUID field must be defined " \
                          "for layer {0}".format(lyr.name)
                    self.commontools.new_message(msg)
                    self.asseticsdk.logger.warning(msg)
                    return None, None, None

        if idfield is not None and idfield not in actuallayerflds:
            msg = "Asset ID Field [{0}] is defined in configuration but is not" \
                  " in layer {1}, check logfile for field list".format(
                idfield, lyr.name)
            self.commontools.new_message(msg)
            self.asseticsdk.logger.warning(msg)
            msg = "Fields in layer {0} are: {1}".format(
                lyr.name, actuallayerflds)
            self.asseticsdk.logger.warning(msg)
            return None, None, None

        return lyr_config, fields, idfield

    def create_asset(self, lyr, query=None):
        """
        For the given layer create new assets for the selected features only if
        features have no assetic guid.
        :param lyr: is the layer to process (not layer name but ArcMap layer)
        :param query: optionally apply query filter
        """
        pass_cnt = 0
        fail_cnt = 0
        self.asseticsdk.logger.debug(
            "create_asset. Layer={0}".format(lyr.name))
        # get configuration for layer
        lyr_config, fields, idfield = self.get_layer_config(lyr, "create")
        if lyr_config is None:
            return

        # get number of records to process for use with timing dialog
        selcount = len(lyr.getSelectionSet())

        if self.commontools.is_desktop:
            if self.config.force_use_arcpy_addmessage:
                # Set the progressor which provides feedback via the script
                # tool dialogue
                arcpy.SetProgressor(
                    "step", "Updating assets for layer {0}".format(
                        lyr.name), 0, selcount, 1)
                # need to set a dummy progress tool because further down need
                # to use a with in case using the pythonaddin.ProgressDialogue
                progress_tool = DummyProgressDialog()
            else:
                # desktop via addin, so give user a progress dialog.
                # This progress tool is set with a 'with' further down
                # This dialogue is slow and a little unreliable for large
                # selection sets.
                progress_tool = pythonaddins.ProgressDialog
        else:
            # not desktop so give use dummy progress dialog.
            progress_tool = DummyProgressDialog()
            selcount = 0

        with progress_tool as dialogtools:
            if self.commontools.is_desktop and \
                    not self.config.force_use_arcpy_addmessage:
                dialog = dialogtools
                dialog.title = "Assetic Integration"
                dialog.description = "Creating Assets for layer {0}.".format(
                    lyr.name)
                dialog.canCancel = False

            # Create update cursor for feature class
            with arcpy.da.UpdateCursor(lyr, fields, query) as cursor:
                cnt = 1.0
                for row in cursor:
                    if self.commontools.is_desktop:
                        if self.config.force_use_arcpy_addmessage:
                            # Using the progressor
                            arcpy.SetProgressorLabel(
                                "Creating Assets for layer {0}.\nProcessing "
                                "feature {1} of {2}".format(
                                    lyr.name, int(cnt), selcount))
                            arcpy.SetProgressorPosition()
                        else:
                            dialog.description = \
                                "Creating Assets for layer {0}." \
                                "\nProcessing feature {1} of {2}".format(
                                    lyr.name, int(cnt), selcount)
                            dialog.progress = cnt / selcount * 100
                    if self._new_asset(row, lyr_config, fields):
                        cursor.updateRow(row)
                        pass_cnt = pass_cnt + 1
                    else:
                        fail_cnt = fail_cnt + 1
                    cnt = cnt + 1

        message = "Finished {0} Asset Creation, {1} Assets created".format(
            lyr.name, str(pass_cnt))
        if fail_cnt > 0:
            message = message + ", {0} assets could not be created " \
                                "(check log file {1})".format(
                str(fail_cnt), self.logfilename)
        self.commontools.new_message(message)

    def update_assets(self, lyr):
        """
        For the given layer update assets for the selected features only
        where features have an assetic guid/asset id.
        :param lyr: is the layer to process (not layer name but ArcMap layer)
        """
        # Script Variables
        iPass = 0
        iFail = 0

        # get layer configuration from xml file
        lyr_config, fields, idfield = self.get_layer_config(lyr, "update")
        if lyr_config is None:
            return

        # get number of records to process for use with timing dialog
        selcount = len(lyr.getSelectionSet())

        if self.commontools.is_desktop:
            if self.config.force_use_arcpy_addmessage:
                # Set the progressor which provides feedback via the script
                # tool dialogue
                arcpy.SetProgressor(
                    "step", "Updating assets for layer {0}".format(
                        lyr.name), 0, selcount, 1)
                # need to set a dummy progress tool becuase futher down need
                # to use a with in case using the pythonaddin.ProgressDialogue
                progress_tool = DummyProgressDialog()
            else:
                # desktop via addin, so give user a progress dialog.
                # This progress tool is set with a 'with' further down
                # This dialogue is slow and a little unreliable for large
                # selection sets.
                progress_tool = pythonaddins.ProgressDialog
        else:
            # not desktop so give use dummy progress dialog.
            progress_tool = DummyProgressDialog()
            selcount = 0
        with progress_tool as dialog:
            if self.commontools.is_desktop and \
                    not self.config.force_use_arcpy_addmessage:
                dialog.title = "Assetic Integration"
                dialog.description = "Updating assets for layer {0}".format(
                    lyr.name)
                dialog.canCancel = False
                # Create update cursor for feature class
            with arcpy.da.SearchCursor(lyr, fields) as cursor:
                cnt = 1.0
                for row in cursor:
                    chk = self._update_asset(row, lyr_config, fields)

                    if self.commontools.is_desktop:
                        if self.config.force_use_arcpy_addmessage:
                            # Using the progressor
                            arcpy.SetProgressorLabel(
                                "Updating Assets for layer {0}.\nProcessing "
                                "feature {1} of {2}".format(
                                    lyr.name, int(cnt), selcount))
                            arcpy.SetProgressorPosition()
                        else:
                            dialog.description = \
                                "Updating Assets for layer {0}." \
                                "\nProcessing feature {1} of {2}".format(
                                    lyr.name, int(cnt), selcount)
                            dialog.progress = cnt / selcount * 100
                    else:
                        msg = "Updating Assets for layer {0}." \
                              "\nProcessing feature {1} of {2}".format(
                            lyr.name, int(cnt), selcount)
                        self.commontools.new_message(msg)
                        self.asseticsdk.logger.info(msg)
                    if not chk:
                        iFail = iFail + 1
                    else:
                        iPass = iPass + 1

                    # increment counter
                    cnt = cnt + 1

        message = "Finished {0} Asset Update, {1} assets updated".format(
            lyr.name, str(iPass))
        if iFail > 0:
            message = "{0}, {1} assets not updated. (Check logfile {2})".format(
                message, str(iFail), self.logfilename)
        self.commontools.new_message(message, "Assetic Integration")

    def display_asset(self, lyr):
        """
        Open assetic and display the first selected feature in layer
        :param lyr: The layer find selected assets.  Not layer name,layer object
        """
        # get layer config details
        lyr_config, fields, idfield = self.get_layer_config(lyr, "display")
        if lyr_config is None:
            return

        self.asseticsdk.logger.debug("Layer: {0}, id field: {1}".format(
            lyr.name, idfield))
        try:
            features = arcpy.da.SearchCursor(lyr, idfield)
            row = features.next()
            assetid = str(row[0])
        except Exception as ex:
            msg = "Unexpected Error Encountered, check log file"
            self.commontools.new_message(msg)
            self.asseticsdk.logger.error(str(ex))
            return
        if assetid is None or assetid.strip() == "":
            msg = "Asset ID or Asset GUID is NULL.\nUnable to display asset"
            self.commontools.new_message(msg)
            self.asseticsdk.logger.warning(str(msg))
            return
        self.asseticsdk.logger.debug("Selected Asset to display: [{0}]".format(
            assetid))
        # Now launch Assetic
        apihelper = assetic.APIHelper(self.asseticsdk.client)
        apihelper.launch_assetic_asset(assetid)

    def _new_asset(self, row, lyr_config, fields):
        """
        Create a new asset for the given search result row
        :param row: a layer search result row, to create the asset for
        :param lyr_config: configuration object for asset field mapping
        :param fields: list of attribute fields
        :returns: Boolean True if success, else False
        """

        complete_asset_obj = self.get_asset_obj_for_row(row, lyr_config,
                                                        fields)

        # alias core fields for readability
        corefields = lyr_config["corefields"]

        # verify it actually needs to be created
        newasset = False
        if "id" in corefields and corefields["id"] in fields:
            if not complete_asset_obj.asset_representation.id:
                # guid field exists in ArcMap and is empty
                newasset = True
            else:
                # guid id populated, must be existing asset
                newasset = False
        else:
            # guid not used, what about asset id?
            if "asset_id" in corefields and corefields["asset_id"] in fields:
                # asset id field exists in Arcmap
                if not complete_asset_obj.asset_representation.asset_id:
                    # asset id is null, must be new asset
                    newasset = True
                else:
                    # test assetic for the asset id.
                    # Perhaps user is not using guid
                    # and is manually assigning asset id.
                    chk = self.assettools.get_asset(
                        complete_asset_obj.asset_representation.asset_id)
                    if not chk:
                        newasset = True
                    else:
                        # asset id already exists.  Not a new asset
                        newasset = False
            else:
                # there is no field in ArcMap representing either GUID or
                # Asset ID, so can't proceed.
                self.asseticsdk.logger.error(
                    "Asset not created because there is no configuration "
                    "setting for <id> or <asset_id> or the field is not in "
                    "the layer")
                return False
        if not newasset:
            self.asseticsdk.logger.warning(
                "Asset not created because it already has the following "
                "values: Asset ID={0},Asset GUID={1}".format(
                    complete_asset_obj.asset_representation.asset_id
                    , complete_asset_obj.asset_representation.id))
            return False

        # set status
        complete_asset_obj.asset_representation.status = \
            lyr_config["creation_status"]
        # Create new asset
        response = self.assettools.create_complete_asset(complete_asset_obj)
        if response is None:
            msg = "Asset Not Created - Check log"
            self.commontools.new_message(msg)
            return False
        # apply asset guid and/or assetid
        if "id" in corefields:
            row[fields.index(corefields["id"])] = \
                response.asset_representation.id
        if "asset_id" in corefields:
            row[fields.index(corefields["asset_id"])] = \
                response.asset_representation.asset_id
        # apply component id
        for component_dim_obj in response.components:
            for component_config in lyr_config["components"]:
                component_type = None
                if "component_type" in component_config["attributes"]:
                    component_type = component_config["attributes"][
                        "component_type"]
                elif "component_type" in component_config["defaults"]:
                    component_type = component_config["defaults"][
                        "component_type"]

                if "id" in component_config["attributes"] and component_type \
                        == component_dim_obj.component_representation \
                        .component_type:
                    row[fields.index(component_config["attributes"]["id"])] = \
                        component_dim_obj.component_representation.id

        # Now check config and update assetic with spatial data and/or address
        addr = None
        geojson = None
        if len(lyr_config["addressfields"]) > 0 \
                or len(lyr_config["addressdefaults"]) > 0:
            # get address details
            addr = assetic.CustomAddress()
            # get address fields from the attribute fields of the feature
            for k, v in six.iteritems(lyr_config["addressfields"]):
                if k in addr.to_dict() and v in fields:
                    setattr(addr, k, row[fields.index(v)])
            # get address defaults
            for k, v in six.iteritems(lyr_config["addressdefaults"]):
                if k in addr.to_dict():
                    setattr(addr, k, v)
        if lyr_config["upload_feature"]:
            geometry = row[fields.index('SHAPE@')]
            centroid = row[fields.index('SHAPE@XY')]
            geojson = self.get_geom_geojson(4326, geometry, centroid)
        if addr or geojson:
            chk = self.assettools.set_asset_address_spatial(
                response.asset_representation.id, geojson, addr)
            if chk > 0:
                return False
        return True

    def _update_asset(self, row, lyr_config, fields):
        """
        Update an existing asset for the given arcmap row
        :param row: a layer search result row, to create the asset for
        :param lyr_config: configuration object for asset field mapping
        :param fields: list of attribute fields
        :returns: Boolean True if success, else False
        """
        complete_asset_obj = self.get_asset_obj_for_row(row, lyr_config,
                                                        fields)

        # alias core fields configuration for readability
        corefields = lyr_config["corefields"]

        # make sure we have an asset id to use
        if not complete_asset_obj.asset_representation.id:
            # guid not used, what about asset id?
            if complete_asset_obj.asset_representation.asset_id:
                # asset id is not null
                # test assetic for the asset id.
                chk = self.assettools.get_asset(
                    complete_asset_obj.asset_representation.asset_id)
                if chk:
                    asset_exists = True
                    # set the guid, need it later if doing spatial load
                    complete_asset_obj.asset_representation.id = chk["Id"]

        if not complete_asset_obj.asset_representation.id:
            self.asseticsdk.logger.debug(
                "Asset not updated because it is undefined or not in Assetic. "
                "Asset ID={0}".format(
                    complete_asset_obj.asset_representation.asset_id))
            return False

        if len(complete_asset_obj.components) > 0:
            # have components, assume network measure needed, also assume we
            # don't have Id's for the components which are needed for update
            current_complete_asset = self.assettools.get_complete_asset(
                complete_asset_obj.asset_representation.id, []
                , ["components", "dimensions"])

            for component in complete_asset_obj.components:
                # get the id from the current record, matching on
                # component type
                new_comp = component.component_representation
                for current_comp_rep in current_complete_asset.components:
                    current_comp = current_comp_rep.component_representation
                    if current_comp.component_type == new_comp.component_type \
                            or current_comp.id == new_comp.id:
                        # set the id and name in case they are undefined
                        new_comp.id = current_comp.id
                        new_comp.name = current_comp.name

                        # Look for dimensions and set dimension Id
                        for dimension in component.dimensions:
                            count_matches = 0
                            for current_dim in current_comp_rep.dimensions:
                                # match on id or (nm type and record
                                # type and shape name)
                                if not dimension.id and \
                                        dimension.network_measure_type == \
                                        current_dim.network_measure_type and \
                                        dimension.record_type == \
                                        current_dim.record_type and \
                                        dimension.shape_name == \
                                        current_dim.shape_name:
                                    # set dimension id and component id
                                    dimension.id = current_dim.id
                                    dimension.component_id = new_comp.id
                                    count_matches += 1
                            if not dimension.id or count_matches > 1:
                                # couldn't find unique id. remove
                                component.dimensions.remove(dimension)
                                self.asseticsdk.logger.warning(
                                    "Unable to update dimension for "
                                    "component {0} because new existing and "
                                    "distinct dimension record was "
                                    "found".format(
                                        new_comp.name))
                if not new_comp.id:
                    # couldn't find component - remove
                    complete_asset_obj.components.remove(component)
                    self.asseticsdk.logger.warning(
                        "Unable to update component for asset {0}".format(
                            complete_asset_obj.asset_representation.asset_id
                        ))

        # now execute the update
        chk = self.assettools.update_complete_asset(complete_asset_obj)
        if chk > 0:
            self.commontools.new_message(
                "Error Updating Asset:{0}, Asset GUID={1}".format(
                    complete_asset_obj.asset_representation.asset_id
                    , complete_asset_obj.asset_representation.id))
            return False

        # Now check config and update Assetic with spatial data
        if lyr_config["upload_feature"]:
            # get address details
            addr = assetic.CustomAddress()
            # get address fields the attribute fields of the feature
            for k, v in six.iteritems(
                    lyr_config["addressfields"]):
                if k in addr.to_dict() and v in fields:
                    setattr(addr, k, row[fields.index(v)])
            # get address defaults
            for k, v in six.iteritems(
                    lyr_config["addressdefaults"]):
                if k in addr.to_dict():
                    setattr(addr, k, v)
            geometry = row[fields.index('SHAPE@')]
            centroid = row[fields.index('SHAPE@XY')]
            geojson = self.get_geom_geojson(4326, geometry, centroid)
            chk = self.assettools.set_asset_address_spatial(
                complete_asset_obj.asset_representation.id, geojson, addr)
            if chk > 0:
                self.commontools.new_message(
                    "Error Updating Asset Address/Location:{0}, Asset GUID={1}"
                    "".format(
                        complete_asset_obj.asset_representation.asset_id
                        , complete_asset_obj.asset_representation.id))
                return False
        return True

    def get_asset_obj_for_row(self, row, lyr_config, fields):
        """
        Prepare a complete asset for the given search result row
        :param row: a layer search result row, to create the asset for
        :param lyr_config: configuration object for asset field mapping
        :param fields: list of attribute fields in the layer
        :returns: assetic.AssetToolsCompleteAssetRepresentation() or None
        """
        # instantiate the complete asset representation to return
        complete_asset_obj = assetic.AssetToolsCompleteAssetRepresentation()

        # create an instance of the complex asset object
        asset = assetic.models.ComplexAssetRepresentation()

        # set status (mandatory field)
        # asset.status = "Active"

        asset.asset_category = lyr_config["asset_category"]

        # set core field values from arcmap fields
        for k, v in six.iteritems(lyr_config["corefields"]):
            if k in asset.to_dict() and v in fields and \
                    row[fields.index(v)] is not None and \
                    str(row[fields.index(v)]).strip() != "":
                setattr(asset, k, row[fields.index(v)])
        # set core field values from defaults
        for k, v in six.iteritems(lyr_config["coredefaults"]):
            if k in asset.to_dict() and str(v).strip() != "":
                setattr(asset, k, v)

        attributes = {}
        # set attributes values from arcmap fields
        if "attributefields" in lyr_config:
            for k, v in six.iteritems(lyr_config["attributefields"]):
                if v in fields and row[fields.index(v)] is not None and \
                        str(row[fields.index(v)]).strip() != "":
                    attributes[k] = row[fields.index(v)]
        # set attribute values from defaults
        for k, v in six.iteritems(lyr_config["attributedefaults"]):
            if str(v).strip() != "":
                attributes[k] = v
        # add the attributes to the asset and the asset to the complete object
        asset.attributes = attributes
        complete_asset_obj.asset_representation = asset

        # create component representations
        for component in lyr_config["components"]:
            comp_tool_rep = assetic.AssetToolsComponentRepresentation()
            comp_tool_rep.component_representation = \
                assetic.ComponentRepresentation()
            for k, v in six.iteritems(component["attributes"]):
                if v in fields and row[fields.index(v)] is not None and \
                        str(row[fields.index(v)]).strip() != "":
                    setattr(comp_tool_rep.component_representation, k
                            , row[fields.index(v)])
            for k, v in six.iteritems(component["defaults"]):
                if k in comp_tool_rep.component_representation.to_dict():
                    setattr(comp_tool_rep.component_representation, k, v)

            # add dimensions to component
            if component["dimensions"] and len(component["dimensions"]) > 0:
                # create an array for the dimensions to be added
                # to the component
                dimlist = list()
                for dimension in component["dimensions"]:
                    # Create an instance of the dimension and set minimum fields
                    dim = assetic.ComponentDimensionRepresentation()
                    for k, v in six.iteritems(dimension["attributes"]):
                        if v in fields and row[fields.index(v)] is not None \
                                and str(row[fields.index(v)]).strip() != "":
                            setattr(dim, k, row[fields.index(v)])
                    for k, v in six.iteritems(dimension["defaults"]):
                        if k in dim.to_dict():
                            setattr(dim, k, v)
                    dimlist.append(dim)

                # Add the dimension array to the component
                comp_tool_rep.dimensions = dimlist

            # add the component array
            complete_asset_obj.components.append(comp_tool_rep)
        return complete_asset_obj

    def get_geom_wkt(self, outsrid, geometry):
        """
        Get the well known text for a geometry in 4326 projection
        :param outsrid: The projection EPSG code to export WKT as (integer)
        :param geometry: The input geometry
        :returns: wkt string of geometry in the specified projection
        """
        tosr = arcpy.SpatialReference(outsrid)
        new_geom = geometry.projectAs(tosr)
        wkt = new_geom.WKT
        return wkt

    def get_geom_geojson(self, outsrid, geometry, centroid=None):
        """
        Get the geojson for a geometry in 4326 projection
        :param outsrid: The projection EPSG code to export WKT as (integer)
        :param geometry: The input geometry
        :param centroid: The geometry centroid, use for polygons in case polygon
        orientation is wrong.  Optional
        :returns: wkt string of geometry in the specified projection
        """
        tosr = arcpy.SpatialReference(outsrid)

        if "curve" in geometry.JSON:
            # arcs and circles not supported by geoJson
            # the WKT doesn't define arcs so use it
            simple_geom = arcpy.FromWKT(geometry.WKT,
                                        geometry.spatialReference)
            new_geom = simple_geom.projectAs(tosr)
        else:
            new_geom = geometry.projectAs(tosr)
        # now convert to geojson
        geojsonstr = arcgis2geojson(new_geom.JSON)
        geojson = json.loads(geojsonstr)
        centroid_geojson = None
        if "type" in geojson and geojson["type"].lower() == "polygon":
            if isinstance(centroid, tuple) and len(centroid) == 2:
                point = arcpy.Point(centroid[0], centroid[1])
                pt_geometry = arcpy.PointGeometry(point
                                                  , geometry.spatialReference)
                new_centroid = pt_geometry.projectAs(tosr)
                centroid_geojson_str = arcgis2geojson(new_centroid.JSON)
                centroid_geojson = json.loads(centroid_geojson_str)
        if "GeometryCollection" not in geojson:
            # Geojson is expected to include collection, but arcgis2geojson
            # does not include it
            if centroid_geojson:
                fullgeojson = {
                    "geometries": [geojson, centroid_geojson]
                    , "type": "GeometryCollection"}
            else:
                fullgeojson = {
                    "geometries": [geojson]
                    , "type": "GeometryCollection"}
        else:
            # not try to include centroid, too messy.  Am not expecting to hit
            # this case unless arcgis2geojson changes
            fullgeojson = geojson
        return fullgeojson

    def _bulk_update_assets(self, lyr, lyr_config, fields):
        """
        Update an existing asset for the given arcmap row
        :param lyr: a layer to process
        :param lyr_config: configuration object for asset field mapping
        :param fields: list of attribute fields
        :returns: Boolean True if success, else False
        """

        # alias core fields configuration for readability
        corefields = lyr_config["corefields"]

        asset_writer = self._set_csv_writer()
        asset_columns = list()
        all_asset_data = list()
        with arcpy.da.SearchCursor(lyr, fields) as cursor:
            cnt = 1.0
            for row in cursor:
                # set the data in the complete asset object
                complete_asset_obj = self.get_asset_obj_for_row(row,
                                                                lyr_config,
                                                                fields)

                # make sure we have an asset id, can't use guid
                if complete_asset_obj.asset_representation.asset_id:
                    # prepare a dictionary of the asset data
                    asset = complete_asset_obj.asset_representation
                    asset_dict = asset.to_dict()
                    if asset_dict["attributes"]:
                        # there is a dict of attributes, get the dict
                        attributes_dict = asset_dict["attributes"]
                        # remove the reference to the dict
                        asset_dict.pop("attributes")
                        # merge the data in the attributes dict
                        asset_dict.update(attributes_dict)
                    # get the dictionary keys (columns) where there is a value
                    columns = [x[0] for x in asset_dict.items() if x[1]]
                    # update the column list that applies to all assets
                    asset_columns = list(set(asset_columns + columns))

                    if len(complete_asset_obj.components) > 0:
                        # have components, assume network measure needed
                        for component in complete_asset_obj.components:
                            # prepare the component update
                            # label in API = "Component Name" in UI
                            # component_type = "ComponentType"
                            # component_name = "Component ID"
                            pass

                            # Look for dimensions and set dimension Id
                            for dimension in component.dimensions:
                                # dimension.network_measure_type
                                # dimension.record_type
                                if dimension.shape_name:
                                    # dimension shape import
                                    pass
                                else:
                                    # dimension no shape import
                                    pass
                else:
                    self.asseticsdk.logger.debug(
                        "Asset not bulk updated because there is no Asset "
                        "Id.")

            if len(all_asset_data) > 0:
                # write asset header columns
                asset_writer.writerow(asset_columns)
            # loop through asset data and write to csv
            for i_r in all_asset_data:
                # map data to column list by key to avoid issues with column order
                # and insert "" for additional columns not in the data
                if six.PY2:
                    asset_writer.writerow(
                        map(lambda x: i_r.get(x).encode('utf-8')
                        if isinstance(i_r.get(x), unicode)
                        else i_r.get(x, "")
                            , asset_columns)
                    )
                else:
                    asset_writer.writerow(list(
                        map(lambda x: i_r.get(x, ""), columns)))

            csvdata = output.getvalue()
            output.close()

        # Now check config and update Assetic with spatial data
        if lyr_config["upload_feature"]:
            # get address details
            addr = assetic.CustomAddress()
            # get address fields the attribute fields of the feature
            for k, v in six.iteritems(
                    lyr_config["addressfields"]):
                if k in addr.to_dict() and v in fields:
                    setattr(addr, k, row[fields.index(v)])
            # get address defaults
            for k, v in six.iteritems(
                    lyr_config["addressdefaults"]):
                if k in addr.to_dict():
                    setattr(addr, k, v)
            geometry = row[fields.index('SHAPE@')]
            centroid = row[fields.index('SHAPE@XY')]
            geojson = self.get_geom_geojson(4326, geometry, centroid)
            chk = self.assettools.set_asset_address_spatial(
                complete_asset_obj.asset_representation.id, geojson, addr)
            if chk > 0:
                self.commontools.new_message(
                    "Error Updating Asset Address/Location:{0}, Asset GUID={1}"
                    "".format(
                        complete_asset_obj.asset_representation.asset_id
                        , complete_asset_obj.asset_representation.id))
                return False
        return True

    def _set_csv_writer(self):
        """
        create a csv writer
        :param self:
        :return: csv writer
        """
        # set csv writer output to string
        if six.PY2:
            output = io.BytesIO()
            writer = csv.writer(output)
        else:
            output = io.StringIO()
            writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
        return writer

    def GetEventAssetID(self, geometryObj, oidList, layerList):
        """
        Gets the guid for an asset feature that has been deleted or moved
        https://github.com/savagemat/PythonEditCounter/blob/master/Install/PythonEditCounter_addin.py
        :param geometryObj: The feature that was deleted or moved
        :param oidList: A list of OIDs as integers
        :param layerList: Layers in the workspace
        :returns: Unique Assetic ID of the feature that was deleted/moved
        """
        assetlayers = {}
        for lyr in layerList:
            if lyr.isFeatureLayer:
                ##get layer config details
                lyr_config, fields, idfield = self.get_layer_config(
                    lyr, "delete")
                if idfield != None:
                    oidField = arcpy.Describe(lyr).OIDFieldName
                    query = "{0} in {1}".format(oidField, str(oidList).replace(
                        '[', '(').replace(']', ')'))
                    with arcpy.da.SearchCursor(lyr,
                                               [oidField, "SHAPE@", idfield],
                                               where_clause=query) as rows:
                        for row in rows:
                            geom = row[1]
                            if geom.JSON == geometryObj.JSON:
                                ##return the assetid and the layer it belongs to
                                return row[2], lyr

        # feature is not a valid asset so return nothing
        return None, None

    def undo_edit(self, lyr):
        """
        Not implemented.  Works outside of edit session but not in
        need to figure out how to access
        """
        desc = arcpy.Describe(lyr)
        workspace = desc.path
        with arcpy.da.Editor(workspace) as edit:
            edit.abortOperation()

    def get_layer_asset_guid(self, assetid, lyr_config):
        """
        Get the asset guid for an asset.  Used where "id" is not in the
        configuration.  If it is then it is assumed the assetid is a guid
        :param assetid: The assetid - may be guid or friendly
        :param lyr_config: the layer
        :returns: guid or none
        """
        # alias core fields object for readability
        corefields = lyr_config["corefields"]
        if "id" not in corefields:
            ##must be using asset_id (friendly).  Need to get guid
            asset = self.assettools.get_asset(assetid)
            if asset != None:
                assetid = asset["Id"]
            else:
                msg = "Asset with ID [{0}] not found in Assetic".format(
                    assetid)
                self.asseticsdk.logger.warning(msg)
                return None
        return assetid

    def set_asset_address_spatial(self, assetid, lyr_config, geojson,
                                  addr=None):
        """
        Set the address and/or spatial definition for an asset
        :param assetid: The asset GUID (TODO support friendly ID)
        :param lyr_config: The settings defined for the layer
        :param geojson: The geoJson representation of the feature
        :param addr: Address representation.  Optional.
        assetic.CustomAddress
        :returns: 0=no error, >0 = error
        """
        if addr is not None and \
                not isinstance(addr, assetic.CustomAddress):
            msg = "Format of address incorrect,expecting " \
                  "assetic.CustomAddress"
            self.asseticsdk.logger.debug(msg)
            return 1
        else:
            addr = assetic.CustomAddress()

        ##get guid
        assetguid = self.get_layer_asset_guid(assetid, lyr_config)
        if assetguid == None:
            msg = "Unable to obtain asset GUID for assetid={0}".format(assetid)
            self.asseticsdk.logger.error(msg)
            return 1
        chk = self.assettools.set_asset_address_spatial(assetguid, geojson,
                                                        addr)
        return 0

    # def get_session_and_baseurl(self):
    #     """
    #     Create a Requests session and also return base url
    #     :returns: tuple, authenticated requests session and base url
    #     """
    #     env_url = self.asseticsdk.client.host
    #     basic_auth = self.asseticsdk.conf.username,self.asseticsdk.conf.password
    #     session = requests.Session()
    #     headers = {'content-type': 'application/json'}
    #     session.headers.update(headers)
    #     session.auth = basic_auth
    #     return session, env_url

    def decommission_asset(self, assetid, lyr_config, comment=None):
        """
        Set the status of an asset to decommisioned
        :param assetid: The asset GUID (TODO support friendly ID)
        :param lyr_config: config details for layer
        :param comment: A comment to accompany the decommision
        :returns: 0=no error, >0 = error
        """

        return 1
        # ##get guid
        # assetguid = self.get_layer_asset_guid(assetid,lyr_config)
        # if assetguid == None:
        #     return 1
        #
        # if comment == None:
        #     comment = "Decommisioned via GIS"
        # if not self.b_use_v1:
        #     msg = "Unable to decommision asset, python requests library needed"\
        #           " when using v1 api"
        #     self.asseticsdk.logger.error(msg)
        #     return 1
        #
        # session,env_url = self.get_session_and_baseurl()
        #
        # # Complex Asset to be updated
        # data = {"DecommissionTriggerCode":60,"Comments":comment}
        #
        # # Encode the data to create a JSON payload
        # payload = json.dumps(data)
        #
        # # Update a Complex Asset
        # url = "{0}/api/ComplexAssetApi/{1}/Decommission/60".format(env_url,
        #                                                            assetguid)
        # try:
        #     response = session.put(url, data=payload)
        # except Exception as ex:
        #     msg = "Decommision asset.  Error message {0}".format(str(ex))
        #     self.asseticsdk.logger.error(msg)
        #     return 1
        # # Check for HTTP codes other than 200 (Created)
        # if response.status_code != 200:
        #     msg = 'Response failed with error {}'.format(str(response))
        #     self.asseticsdk.logger.error(msg)
        #     return response.status_code
        # else:
        #     return 0
