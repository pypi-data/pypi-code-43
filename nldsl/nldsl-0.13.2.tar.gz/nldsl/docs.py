# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

"""A collection of doc strings shared between grammar rules."""




EXPRESSION_ONLY_DOC = """Parses python expressions outside of a pipeline.

Examples:
    1. x = 5
    2. x = y % (5.7 + z / 2)
    3. x = w and (y or not z)

Grammar:
    !expr

Args:
    expr (expression): The expression to be evaluated.

Type:
    Function
"""


ON_DF_DOC = """Starts a pipeline on the given DataFrame.

Examples:
    1. x = on df
    2. x = on df | transformer 1 ... | transformer n ... | operation

Grammar:
    on $dataframe

Args:
    dataframe (variable): The name of DataFrame

Type:
    Initialization
"""


CREATE_DF_DOC = """Creates a new DataFrame from an list.

Examples:
    1. x = create dataframe from my_data with header 'col1', 'col2', 'col3'

Grammar:
    create dataframe from $data with header $header[$col_name]

Args:
    data (variable): The data from which to create the dataframe.
    header (list): A list of column names

Type:
    Initialization
"""


LOAD_FROM_DOC = """Load a DataFrame from a file.

Examples:
    1. x = load from "my_file.json" as json
    2. x = load from "my_file.csv" as csv | drop duplicates

Grammar:
    load from $path as $type
    type := { json, csv }

Args:
    path (variable): A string containing the path to a file.
    type (variable): The type of the file.

Type:
    Initialization
"""


SAVE_TO_DOC = """Save a DataFrame to a file.

Examples:
    1. on df | save to "my_file.json" as json
    2. on df | save to "my_file.csv" as csv

Grammar:
    save to $path as $type
    type := { json, csv }

Args:
    path (variable): A string containing the path to a file.
    type (variable): The type of the file.

Type:
    Operation
"""


UNION_DOC = """Compute the union of rows.

Examples:
    1. x = on df | union other

Grammar:
    union $table

Args:
    table (variable): The table from which all rows will be added.

Type:
    Transformation
"""


DIFFERENCE_DOC = """Remove all rows which are contained in `table`.

Examples:
    1. x = on df | difference other

Grammar:
    difference $table

Args:
    table (variable): The table which contains all rows that shall be removed.

Type:
    Transformation
"""


INTERSECTION_DOC = """Remove all rows which are not contained in `table`.

Examples:
    1. x = on df | intersection other

Grammar:
    intersection $table

Args:
    table (variable): The table which contains all rows that shall not be removed.

Type:
    Transformation
"""


JOIN_DOC = """Compute join with this DataFrame.

Examples:
    1. x = on df | join inner df2 on 'col1', 'col2'
    2. x = on df | join left df2 on 'col1'

Grammar:
    join $how $table on $columns[$col]
    how := { left, right, outer, inner }

Args:
    how (variable): How the join shall be performed.
    table (variable): The table with which to join.
    columns (varlist): A list of column on which to join.

Type:
    Transformation
"""


SELECT_COLUMNS_DOC = """Select certain columns from a DataFrame.

Examples:
    1. ## x = on df | select columns df.col1, col2, df.col3
    2. ## x = on df | select columns "col1", "col2", "col3"

Grammar:
    select columns $columns[$col]

Args:
    columns (varlist): A list of column names.

Type:
    Transformation
"""


SELECT_ROWS_DOC = """Select the rows of a DataFrame based on some condition.

The condition can be composed out of boolean, comparison and arithmetic
expression. The operator precedence is equivalent to python and it is possible
to use brackets to modify it.

Examples:
    1. ## x = on df | select rows df.col1 > (14.2 + z) and df.col2 == 'A'
    2. ## x = on df | select rows df.col1 != 0 and not df.col2 in [3, 5, 7]
    3. ## x = on df | select rows df.col3 % df.col1 != 2 or df.col1 <= 12

Grammar:
    select rows !condition

Args:
    condition (expression): A boolean expression used as a row filter.

Type:
    Transformation
"""


DROP_COLUMNS_DOC = """Drop certain columns from a DataFrame.

Examples:
    1. ## x = on df | drop columns df.col1, col2, df.col3
    2. ## x = on df | drop columns "col1", "col2", "col3"

Grammar:
    drop columns $columns[$col]

Args:
    columns (varlist): A list of column names.

Type:
    Transformation

"""


GROUP_BY_DOC = """Group a DataFrame and apply an aggregation.

Examples:
    1. ## x = on df | group by df.col1 apply min
    2. ## x = on df | group by df.col1, df.col2 apply mean

Grammar:
    group by $columns[$col] apply $aggregation
    aggregation := { min, max, sum, avg, mean, count }

Args:
    columns (varlist): A list of column names.
    aggregation (variable): The aggregation operation to be performed.
Type:
    Operation
"""


REPLACE_VALUES_DOC = """Replace a value with another.

Every occurrence of `old_value` will be substituted with `new_value`.

Examples:
    1. ## x = on df | replace values 1 by 0
    2. ## x = on df | replace values "old" by "new"

Grammar:
    replace $old_value with $new_value

Args:
    old_value (variable): The value to be replaced.
    new_value (variable): The value it will be replaced with.

Type:
    Operation
"""


APPEND_COLUMN_DOC = """Append a new column to the DataFrame.

Example:
    1. x = on df | append column df.col1 * 2 as 'new_col'

Grammar:
    append column !col_expr as $col_name

Args:
    col_expr (expression): An expression defining the new value of the column.
    col_name (variable): The new name of the column.

Type:
    Transformation
"""


SORT_BY_DOC = """Sort the DataFrame by certain columns.

Examples:
    1. ## x = on df | sort by df.col1 descending
    2. ## x = on df | sort by "col1" ascending, "col2" descending

Grammar:
    sort by $columns[$col $order]
    order := { ascending, descending }

Args:
    columns (varlist): A list of column names and sorting order pairs.

Type:
    Transformation
"""


DROP_DUPLICATES_DOC = """Drop duplicate rows from a DataFrame.

Examples:
    1. x = on df | drop duplicates
    2. x = on df | select rows df.col1 != 0 | drop duplicates

Grammar:
    drop duplicates

Type:
    Transformation
"""


RENAME_COLUMNS_DOC = """Rename some columns in a DataFrame.

Examples:
    1. x = on df | rename columns col1 to col2
    2. x = on df | rename columns col1 to col2, col3 to col4 | show

Grammar:
    rename columns $columns[$current to $new]

Args:
    columns (list): A list of current and new column names.

Type:
    Transformation
"""


SHOW_DOC = """Print the DataFrame to stdout.

Examples:
    1. on df | show
    2. on df | drop duplicates | show

Grammar:
    show

Type:
    Operation
"""


SHOW_SCHEMA_DOC = """Print the schema of the DataFrame to stdout.

Examples:
    1. on df | show schema

Grammar:
    show schema

Type:
    Operation
"""


DESCRIBE_DOC = """Print a description of the DataFrame to stdout.

Examples:
    1. on df | describe
    2. on df | drop duplicates | describe

Grammar:
    describe

Type:
    Operation
"""


HEAD_DOC = """Get the `num_rows` top most rows in the DataFrame.

Examples:
    1. on df | head 10
    2. on df | drop duplicates | head 100

Grammar:
    head $num_rows

Args:
    num_rows (variable): The number of rows to return.

Type:
    Operation
"""


COUNT_DOC = """Count the number of rows in the DataFrame.

Examples:
    1. on df | count
    2. on df | drop duplicates | count

Grammar:
    count

Type:
    Operation
"""
