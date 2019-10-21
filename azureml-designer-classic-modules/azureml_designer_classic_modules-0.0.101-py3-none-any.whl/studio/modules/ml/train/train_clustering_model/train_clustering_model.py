import pandas as pd

import azureml.studio.modules.ml.common.ml_utils as ml_utils
from azureml.studio.modulehost.attributes import UntrainedClusterInputPort, DataTableInputPort, ColumnPickerParameter, \
    BooleanParameter, ModuleMeta, ReleaseState, IClusterOutputPort, SelectedColumnCategory, DataTableOutputPort
from azureml.studio.common.datatable.data_table import DataTableColumnSelection
from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.error import ErrorMapping, TooFewRowsInDatasetError, TooFewFeatureColumnsInDatasetError
from azureml.studio.common.input_parameter_checker import InputParameterChecker
from azureml.studio.core.logger import module_logger
from azureml.studio.modulehost.module_reflector import module_entry, BaseModule
from azureml.studio.modules.ml.initialize_models.cluster.kmeans_cluster.kmeans_cluster import KMeansCluster, \
    KMeansCentroidInit


class TrainClusteringModelModule(BaseModule):
    @staticmethod
    @module_entry(ModuleMeta(
        name="Train Clustering Model",
        description="Train clustering model and assign data to clusters",
        category="Machine Learning\\Train",
        version="2.0",
        owner="Microsoft Corporation",
        family_id="BB43C744-F7FA-41D0-AE67-74AE75DA3FFD",
        release_state=ReleaseState.Release,
        is_deterministic=True,
    ))
    def run(
            cluster: UntrainedClusterInputPort(
                name="Untrained model",
                friendly_name="Untrained model",
                description="Untrained clustering model",
            ),
            training_data: DataTableInputPort(
                name="Dataset",
                friendly_name="Dataset",
                description="Input data source",
            ),
            column_set: ColumnPickerParameter(
                name="Column Set",
                friendly_name="Column set",
                description="Column selection pattern",
                column_picker_for="Dataset",
                single_column_selection=False,
                column_selection_categories=(SelectedColumnCategory.All,),
            ),
            append_or_result_only: BooleanParameter(
                name="Check for Append or Uncheck for Result Only",
                friendly_name="Check for append or uncheck for result only",
                description="Whether output dataset must contain input dataset appended by assignments "
                            "column (Checked) or assignments column only (Unchecked)",
                default_value=True,
            )
    ) -> (
            IClusterOutputPort(
                name="Trained model",
                friendly_name="Trained model",
                description="Trained clustering model",
            ),
            DataTableOutputPort(
                name="Results dataset",
                friendly_name="Results dataset",
                description="Input dataset appended by data column of assignments or assignments column only",
            ),
    ):
        input_values = locals()
        output_values = TrainClusteringModelModule.train_clustering_model(**input_values)
        return output_values

    @classmethod
    def _validate_args(cls, learner, training_data, column_set):
        InputParameterChecker.verify_data_table(data_table=training_data,
                                                friendly_name=cls._args.training_data.friendly_name)
        column_indexes = column_set.select_column_indexes(training_data)
        if len(column_indexes) < 1:
            ErrorMapping.throw(
                TooFewFeatureColumnsInDatasetError(required_columns_count=1,
                                                   arg_name=cls._args.training_data.friendly_name))

        # if user only selects the label column, module will get 0 feature columns.
        if len(column_indexes) == 1 and \
                training_data.meta_data.label_column_name == training_data.get_column_name(column_indexes[0]):
            ErrorMapping.throw(
                TooFewFeatureColumnsInDatasetError(required_columns_count=1,
                                                   arg_name=cls._args.training_data.friendly_name))

    @classmethod
    def train_clustering_model(cls, cluster: KMeansCluster, training_data: DataTable,
                               column_set: DataTableColumnSelection, append_or_result_only):
        module_logger.info("Validate input data (learner and training data).")
        cls._validate_args(cluster, training_data, column_set)
        # reset index of input data table
        training_data.data_frame.reset_index(drop=True, inplace=True)
        label_column_name = training_data.meta_data.label_column_name
        label_column = None if label_column_name is None \
            else training_data.get_column(label_column_name)
        # get a copy of sub-DataTable
        selected_data = column_set.select(training_data)

        # TODO: init with label mode
        # if label_column_name not in training_data.column_names:
        #    selected_data.add_column(label_column_name, label_column)
        if cluster.setting.kmeans_centroid_init not in (
                KMeansCentroidInit.Random, KMeansCentroidInit.KMeansPP, KMeansCentroidInit.Default):
            raise NotImplementedError()

        input_df = selected_data.data_frame
        # numeric feature should not contain nan, get all validate instance indexes.
        valid_row_indexes = ml_utils.collect_notna_numerical_feature_instance_row_indexes(
            data_table=selected_data,
            label_column_name=label_column_name,
            include_inf=True
        )
        module_logger.info(f'Found {len(valid_row_indexes)} row(s) without missing numerical feature.')
        if len(valid_row_indexes) < cluster.setting.noc:
            ErrorMapping.throw(TooFewRowsInDatasetError(arg_name=cls._args.training_data.friendly_name,
                                                        required_rows_count=cluster.setting.noc,
                                                        actual_rows_count=len(valid_row_indexes),
                                                        row_type='not NA numerical features'
                                                        ))
        # get a copy of valid training data
        df = input_df.iloc[valid_row_indexes, :].reset_index(drop=True)
        if label_column_name is not None:
            label_column = label_column[valid_row_indexes].reset_index(drop=True)

        try:
            cluster.train(df=df, label_column_name=label_column_name)
        except Exception as e:
            raise e
        assignments, distance_df = cluster.predict(df=df)
        # if label column is given, cluster label could be found.
        if label_column is not None:
            cluster.build_cluster_label(label_column, distance_df)
        # if cluster label is valid, try to reassign label column according to Assign Label Mode.
        if cluster.cluster_label is not None:
            new_label_column = cluster.reassign_label(label_column, assignments)
        else:
            new_label_column = label_column

        # rebuild output df
        predict_df = pd.concat([pd.DataFrame(assignments), distance_df], axis=1)
        predict_df.index = valid_row_indexes
        score_column_names = ml_utils.generate_score_column_meta(predict_df=predict_df,
                                                                 task_type=ml_utils.TaskType.Cluster)
        if append_or_result_only:
            result_df = ml_utils.append_predict_result(data_table=training_data, predict_df=predict_df,
                                                       valid_row_indexes=valid_row_indexes)
        else:
            base_df = pd.DataFrame(index=training_data.data_frame.index)
            result_df = pd.concat([base_df, predict_df], axis=1)
        # if new label column is existing, replace the old one.
        if new_label_column is not None:
            result_df.loc[valid_row_indexes, label_column_name] = new_label_column

        result_data = DataTable(result_df)
        if label_column is not None:
            result_data.meta_data.label_column_name = label_column_name
        result_data.meta_data.score_column_names = score_column_names
        return tuple([cluster, result_data])
