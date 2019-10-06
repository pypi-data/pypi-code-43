'''
ProgramBundle is a Bundle type that inherits from UploadedBundle and adds a
new metadata key, architectures.

When a RunBundle is constructed, its program_target must be in a ProgramBundle.
'''
from codalab.bundles.uploaded_bundle import UploadedBundle
from codalab.objects.metadata_spec import MetadataSpec

# This class will eventually be deprecated.
class ProgramBundle(UploadedBundle):
    BUNDLE_TYPE = 'program'
    METADATA_SPECS = list(UploadedBundle.METADATA_SPECS)
