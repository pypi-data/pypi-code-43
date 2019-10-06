# -*- coding: utf-8 -*-
"""Google Cloud Asset Inventory API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class CloudAssetInventory(Base):
    """CloudAssetInventory class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.asset = build('cloudasset', 'v1', credentials=credentials)
        self.credentials = credentials

    def export_asset_inventory(
        self,
        parent,
        uri='',
        uriPrefix='',
        assetTypes=[],
        contentType='',
    ):
        """Export new asset inventory."""
        body = {
            # 'assetTypes': assetTypes,
            # 'contentType': contentType,
            'outputConfig': {
                'gcsDestination': {
                    # 'uri': uri,
                    # 'uriPrefix': uriPrefix,
                }
            }
        }

        # asset types
        if assetTypes:
            body['assetTypes'] = assetTypes

        # content type
        if contentType:
            body['contentType'] = contentType

        # gcs destination uri or prefix
        if uri:
            body['outputConfig']['gcsDestination']['uri'] = uri
        else:
            body['outputConfig']['gcsDestination']['uriPrefix'] = uriPrefix

        v1 = self.asset.v1()
        return v1.exportAssets(parent=parent, body=body).execute()

    def get_operation(self, name):
        """Get the status of an asset inventory export operation."""
        operations = self.asset.operations()
        return operations.get(name=name).execute()
