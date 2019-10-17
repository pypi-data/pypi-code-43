import itertools
import math
import pandas as pd
import pytest

from azureml.studio.common.datatable.data_table import DataTable
from azureml.studio.common.datatable.data_table import DataTableColumnSelectionBuilder as CSB
from azureml.studio.modules.datatransform.partition_and_sample.partition_and_sample \
    import SampleMethods, PartitionMethods, TrueFalseType, PartitionAndSampleModule, _META_PROPERTY_KEY
from azureml.studio.common.error import GreaterThanOrEqualToError, NotInRangeValueError, ParameterParsingError, \
    InvalidDatasetError, TooFewRowsInDatasetError


@pytest.fixture
def input_data_table():
    return DataTable(
        pd.DataFrame(
            columns=["A", "B"],
            data=[[x, x] for x in range(0, 100)],
            index=["x"+str(i+42) for i in range(0, 100)]
        ))


@pytest.fixture
def input_data_table2():
    col_a = list(itertools.chain.from_iterable([itertools.repeat(v, 100000) for v in [float('nan'), 1, 2, 3]]))
    col_b = list(range(0, len(col_a)))
    return DataTable(
        pd.DataFrame(data={
            "A": col_a,
            "B": col_b,
            "C": col_b,
            "D": col_b,
            "E": col_b,
        }))


@pytest.fixture
def column_selection_a():
    return CSB().include_col_names("A").build()


def test_success_split_and_pick_even(input_data_table):
    num_partitions = 3
    # pylint: disable=no-value-for-parameter
    dt = PartitionAndSampleModule.run(
        table=input_data_table,
        method=SampleMethods.NFoldSplit,
        with_replacement=False,
        random_flag=False,
        seed=0,
        partition_method=PartitionMethods.EvenSizePartitioner,
        num_partitions=num_partitions,
        stratify_flag1=TrueFalseType.FALSE
    )[0]

    assert _META_PROPERTY_KEY in dt.meta_data.extended_properties
    assert len(dt.meta_data.extended_properties[_META_PROPERTY_KEY]) == num_partitions

    # pylint: disable=no-value-for-parameter
    dt_folds = [PartitionAndSampleModule.run(
        table=dt,
        method=SampleMethods.FoldPicker,
        fold_index=i+1,
        pick_complement=False)[0] for i in range(0, num_partitions)]

    fold_row_counts = [dt_ford.number_of_rows for dt_ford in dt_folds]
    sum_rows = sum(fold_row_counts)
    assert sum_rows == input_data_table.number_of_rows
    mean_row_count = dt.number_of_rows / num_partitions
    assert all(math.floor(mean_row_count) <= x <= math.ceil(mean_row_count) for x in fold_row_counts)
    assert all([_META_PROPERTY_KEY not in dt_ford.meta_data.extended_properties for dt_ford in dt_folds])

    all_items = set(itertools.chain.from_iterable([set(dt_fold.data_frame['A']) for dt_fold in dt_folds]))
    assert len(all_items) == dt.number_of_rows


def test_success_split_and_pick_custom(input_data_table):
    folds_list = "0.1,0.3,0.5"
    num_partitions = 4
    # pylint: disable=no-value-for-parameter
    dt = PartitionAndSampleModule.run(
        table=input_data_table,
        method=SampleMethods.NFoldSplit,
        with_replacement=False,
        random_flag=False,
        seed=0,
        partition_method=PartitionMethods.CustomizedPartitioner,
        folds_prop_list=folds_list,
        stratify_flag2=TrueFalseType.FALSE
    )[0]

    assert dt.meta_data.extended_properties[_META_PROPERTY_KEY]
    assert len(dt.meta_data.extended_properties[_META_PROPERTY_KEY]) == num_partitions

    # test pick
    # pylint: disable=no-value-for-parameter
    dt_folds = [PartitionAndSampleModule.run(
        table=dt,
        method=SampleMethods.FoldPicker,
        fold_index=i+1,
        pick_complement=False)[0] for i in range(0, num_partitions)]

    fold_row_counts = [dt_ford.number_of_rows for dt_ford in dt_folds]
    sum_rows = sum(fold_row_counts)
    assert sum_rows == input_data_table.number_of_rows
    assert fold_row_counts == [10, 30, 50, 10]

    all_items = set(itertools.chain.from_iterable([set(dt_fold.data_frame['A']) for dt_fold in dt_folds]))
    assert len(all_items) == dt.number_of_rows

    # test pick complement
    # pylint: disable=no-value-for-parameter
    dt_folds_complement = [PartitionAndSampleModule.run(
        table=dt,
        method=SampleMethods.FoldPicker,
        fold_index=i + 1,
        pick_complement=True)[0] for i in range(0, num_partitions)]

    fold_row_counts_complement = [dt_ford.number_of_rows for dt_ford in dt_folds_complement]
    assert fold_row_counts_complement == [90, 70, 50, 90]


def test_success_split_and_pick_random(input_data_table):
    num_partitions = 3
    # pylint: disable=no-value-for-parameter
    dt = PartitionAndSampleModule.run(
        table=input_data_table,
        method=SampleMethods.NFoldSplit,
        with_replacement=False,
        random_flag=True,
        seed=0,
        partition_method=PartitionMethods.EvenSizePartitioner,
        num_partitions=num_partitions,
        stratify_flag1=TrueFalseType.FALSE
    )[0]

    assert _META_PROPERTY_KEY in dt.meta_data.extended_properties
    assert len(dt.meta_data.extended_properties[_META_PROPERTY_KEY]) == num_partitions

    # pylint: disable=no-value-for-parameter
    dt_folds = [PartitionAndSampleModule.run(
        table=dt,
        method=SampleMethods.FoldPicker,
        fold_index=i+1,
        pick_complement=False)[0] for i in range(0, num_partitions)]

    sum_rows = sum([dt_ford.number_of_rows for dt_ford in dt_folds])
    assert sum_rows == input_data_table.number_of_rows
    assert all([_META_PROPERTY_KEY not in dt_ford.meta_data.extended_properties for dt_ford in dt_folds])

    all_items = set(itertools.chain.from_iterable([set(dt_fold.data_frame['A']) for dt_fold in dt_folds]))
    assert len(all_items) == dt.number_of_rows


def test_success_split_and_pick_random_replacement(input_data_table):
    num_partitions = 3
    # pylint: disable=no-value-for-parameter
    dt = PartitionAndSampleModule.run(
        table=input_data_table,
        method=SampleMethods.NFoldSplit,
        with_replacement=True,
        random_flag=True,
        seed=0,
        partition_method=PartitionMethods.EvenSizePartitioner,
        num_partitions=num_partitions,
        stratify_flag1=TrueFalseType.FALSE
    )[0]

    assert _META_PROPERTY_KEY in dt.meta_data.extended_properties
    assert len(dt.meta_data.extended_properties[_META_PROPERTY_KEY]) == num_partitions

    # pylint: disable=no-value-for-parameter
    dt_folds = [PartitionAndSampleModule.run(
        table=dt,
        method=SampleMethods.FoldPicker,
        fold_index=i+1,
        pick_complement=False)[0] for i in range(0, num_partitions)]

    sum_rows = sum([dt_ford.number_of_rows for dt_ford in dt_folds])
    assert sum_rows == input_data_table.number_of_rows
    assert all([_META_PROPERTY_KEY not in dt_ford.meta_data.extended_properties for dt_ford in dt_folds])


def test_success_split_stratify_even(input_data_table2, column_selection_a):
    num_partitions = 3

    # pylint: disable=no-value-for-parameter
    dt = PartitionAndSampleModule.run(
        table=input_data_table2,
        method=SampleMethods.NFoldSplit,
        with_replacement=False,
        random_flag=False,
        seed=0,
        partition_method=PartitionMethods.EvenSizePartitioner,
        num_partitions=num_partitions,
        stratify_flag1=TrueFalseType.TRUE,
        strats_column1=column_selection_a
    )[0]

    assert _META_PROPERTY_KEY in dt.meta_data.extended_properties
    assert len(dt.meta_data.extended_properties[_META_PROPERTY_KEY]) == num_partitions

    # pylint: disable=no-value-for-parameter
    dt_folds = [PartitionAndSampleModule.run(
        table=dt,
        method=SampleMethods.FoldPicker,
        fold_index=i + 1,
        pick_complement=False)[0] for i in range(0, num_partitions)]

    sum_rows = sum([dt_ford.number_of_rows for dt_ford in dt_folds])
    assert sum_rows == input_data_table2.number_of_rows
    assert all([_META_PROPERTY_KEY not in dt_ford.meta_data.extended_properties for dt_ford in dt_folds])


def test_success_sample(input_data_table):
    rate = 0.2
    # pylint: disable=no-value-for-parameter
    dt = PartitionAndSampleModule.run(
        table=input_data_table,
        method=SampleMethods.Sampling,
        rate=rate,
        seed_sampling=0,
        stratify_flag3=TrueFalseType.FALSE,
    )[0]

    assert dt.number_of_rows == round(input_data_table.number_of_rows * rate)


def test_success_sample_stratify(input_data_table2, column_selection_a):
    rate = 0.2
    # pylint: disable=no-value-for-parameter
    dt = PartitionAndSampleModule.run(
        table=input_data_table2,
        method=SampleMethods.Sampling,
        rate=rate,
        seed_sampling=0,
        stratify_flag3=TrueFalseType.TRUE,
        strats_column3=column_selection_a
    )[0]

    assert dt.number_of_rows == round(input_data_table2.number_of_rows * rate)


def test_success_head(input_data_table):
    head = 20
    # pylint: disable=no-value-for-parameter
    dt = PartitionAndSampleModule.run(
        table=input_data_table,
        method=SampleMethods.Head,
        head_num_rows=head
    )[0]

    assert dt.number_of_rows == head
    assert input_data_table.data_frame.iloc[0:head].equals(dt.data_frame)


def test_success_head_2(input_data_table):
    head = input_data_table.number_of_rows + 10
    # pylint: disable=no-value-for-parameter
    dt = PartitionAndSampleModule.run(
        table=input_data_table,
        method=SampleMethods.Head,
        head_num_rows=head
    )[0]

    expect_row_count = min(input_data_table.number_of_rows, head)
    assert dt.number_of_rows == expect_row_count
    assert input_data_table.data_frame.iloc[0:expect_row_count].equals(dt.data_frame)


def test_error_split(input_data_table):
    folds_list = "xxx"

    with pytest.raises(ParameterParsingError):
        # pylint: disable=no-value-for-parameter
        PartitionAndSampleModule.run(
            table=input_data_table,
            method=SampleMethods.NFoldSplit,
            with_replacement=False,
            random_flag=False,
            seed=0,
            partition_method=PartitionMethods.CustomizedPartitioner,
            folds_prop_list=folds_list,
            stratify_flag2=TrueFalseType.FALSE
        )


def test_error_split_2(input_data_table):
    folds_list = "-0.1,0.5"

    with pytest.raises(NotInRangeValueError):
        # pylint: disable=no-value-for-parameter
        PartitionAndSampleModule.run(
            table=input_data_table,
            method=SampleMethods.NFoldSplit,
            with_replacement=False,
            random_flag=False,
            seed=0,
            partition_method=PartitionMethods.CustomizedPartitioner,
            folds_prop_list=folds_list,
            stratify_flag2=TrueFalseType.FALSE
        )


def test_error_split_partition_num_greater_than_sample_num(input_data_table):
    with pytest.raises(TooFewRowsInDatasetError):
        # pylint: disable=no-value-for-parameter
        PartitionAndSampleModule.run(
            table=input_data_table,
            method=SampleMethods.NFoldSplit,
            with_replacement=False,
            random_flag=False,
            seed=0,
            partition_method=PartitionMethods.EvenSizePartitioner,
            num_partitions=101,
            stratify_flag1=TrueFalseType.FALSE
        )


def test_error_pick(input_data_table):
    # pylint: disable=no-value-for-parameter
    with pytest.raises(InvalidDatasetError):
        PartitionAndSampleModule.run(
            table=input_data_table,
            method=SampleMethods.FoldPicker,
            fold_index=1,
            pick_complement=False)


def test_error_pick_2(input_data_table):
    num_partitions = 3
    # pylint: disable=no-value-for-parameter
    dt = PartitionAndSampleModule.run(
        table=input_data_table,
        method=SampleMethods.NFoldSplit,
        with_replacement=False,
        random_flag=False,
        seed=0,
        partition_method=PartitionMethods.EvenSizePartitioner,
        num_partitions=num_partitions,
        stratify_flag1=TrueFalseType.FALSE
    )[0]

    fold_index = num_partitions + 1
    with pytest.raises(InvalidDatasetError):
        # pylint: disable=no-value-for-parameter
        PartitionAndSampleModule.run(
            table=dt,
            method=SampleMethods.FoldPicker,
            fold_index=fold_index,
            pick_complement=False)


def test_error_sample(input_data_table):
    rate = 1.5

    with pytest.raises(NotInRangeValueError):
        # pylint: disable=no-value-for-parameter
        PartitionAndSampleModule.run(
            table=input_data_table,
            method=SampleMethods.Sampling,
            rate=rate,
            seed_sampling=0,
            stratify_flag3=TrueFalseType.FALSE,
        )

    rate = -0.5

    with pytest.raises(NotInRangeValueError):
        # pylint: disable=no-value-for-parameter
        PartitionAndSampleModule.run(
            table=input_data_table,
            method=SampleMethods.Sampling,
            rate=rate,
            seed_sampling=0,
            stratify_flag3=TrueFalseType.FALSE,
        )


def test_error_head(input_data_table):
    head = -1

    with pytest.raises(GreaterThanOrEqualToError):
        # pylint: disable=no-value-for-parameter
        PartitionAndSampleModule.run(
            table=input_data_table,
            method=SampleMethods.Head,
            head_num_rows=head
        )


def test_bug_fix_476541():
    df = pd.DataFrame({
        "A": list(range(100)) + ['M']
    })
    dt = DataTable(df)

    # test fold split
    # pylint: disable=no-value-for-parameter
    dt_partition = PartitionAndSampleModule.run(
        table=dt,
        method=SampleMethods.NFoldSplit,
        with_replacement=False,
        random_flag=False,
        seed=0,
        partition_method=PartitionMethods.EvenSizePartitioner,
        num_partitions=10,
        stratify_flag1=TrueFalseType.FALSE
    )[0]

    # test fold picker
    # pylint: disable=no-value-for-parameter
    PartitionAndSampleModule.run(
        table=dt_partition,
        method=SampleMethods.FoldPicker,
        fold_index=1,
        pick_complement=False
    )

    # test random sampling
    # pylint: disable=no-value-for-parameter
    PartitionAndSampleModule.run(
        table=dt,
        method=SampleMethods.Sampling,
        rate=0.01,
        seed_sampling=0,
        stratify_flag3=TrueFalseType.FALSE,
    )

    # test top_n_rows
    # pylint: disable=no-value-for-parameter
    PartitionAndSampleModule.run(
        table=dt,
        method=SampleMethods.Head,
        head_num_rows=1
    )
