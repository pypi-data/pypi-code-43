from azureml.studio.modulehost.attributes import DataTableInputPort, ModuleMeta, ReleaseState, DataTableOutputPort
from azureml.studio.modulehost.module_reflector import BaseModule, module_entry


class ProfileDatasetModule(BaseModule):

    @staticmethod
    @module_entry(ModuleMeta(
        name="Profile Dataset",
        description="Generate visualization and schema files of dataset",
        category="Control Flow",
        version="1.0",
        owner="Microsoft Corporation",
        family_id="8ef2968c-54fd-11e9-8647-d663bd873d93",
        release_state=ReleaseState.Alpha,
        is_deterministic=True,
    ))
    def run(
            data_table: DataTableInputPort(
                name="Dataset",
                friendly_name="Dataset",
                description="Input dataset",
            )
    ) -> (
            DataTableOutputPort(
                name="Results dataset",
                friendly_name="Results dataset",
                description="Results dataset",
            ),

    ):
        return data_table,
