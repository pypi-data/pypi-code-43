import os
import typing

def table(
    columns: typing.Iterable[str],
    rows: typing.Iterable[typing.Iterable[object]],
    *,
    title: str = None,
    buffer: int = 2
):
    """ Render a basic table

    Params:
        columns (Iterable[str]): The columns of the table
        rows (Iterable[Iterable[object]]): An iterable providing rows with arbitrary typed
        *,
        title (str): --
        buffer (int): The white space to be added to a column's width after setting width to the largest column entry
    """

    # Determine the width of the window
    _, terminalWidth = os.popen('stty size', 'r').read().split()
    terminalWidth = int(terminalWidth)
    tprint = lambda x: print(x) if len(x) < terminalWidth else print(x[:terminalWidth - 4] + '...')

    # Determine the columns widths
    columnWidths = [0]*len(columns)
    for row in [columns] + rows:
        for i in range(len(columns)):
            columnWidths[i] = max(columnWidths[i], len(str(row[i])))
    columnWidths = [x + buffer for x in columnWidths]

    # define the row formats
    rowTemplate = '|'.join(['{'+str(i)+':^{'+str(i + len(columns))+'}}' for i in range(len(columns))])

    header = rowTemplate.format(*columns, *columnWidths)
    print()

    if title is not None:
        width = min(terminalWidth, len(header))
        print("{0:^{1}}".format(title, width))
        print('='*width)

    tprint(header)
    tprint('='*len(header))
    for row in rows:
        tprint(rowTemplate.format(*[str(x) for x in row], *columnWidths))
    print()