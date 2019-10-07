import gspread
import time
import typing

from .cache import cache
from .log import logger

__all__ = ["Worksheet"]


class Worksheet:
    @cache(key=lambda self, *args, **kwargs: (self.worksheet.id, args, kwargs))
    def get_cell(self, col, row) -> gspread.Cell:
        retries = [305, 135, 35]
        while True:
            try:
                return self.worksheet.cell(col, row)
            except KeyboardInterrupt:
                raise
            except:
                if not retries:
                    logger.warn("Worksheet #%s: error getting cell (%s, %s).  Out of quota?", self.worksheet.id, col, row)
                    raise

                delay = retries.pop()
                logger.warn("Worksheet #%s: error getting cell (%s, %s).  Out of quota?  retrying again in %s seconds!", self.worksheet.id, col, row, delay)
                time.sleep(delay)

    @cache(key=lambda self, *args, **kwargs: (self.worksheet.id, args, kwargs))
    def get_row(self, row, min_col=2) -> typing.List[gspread.Cell]:
        retries = [305, 135, 35]
        while True:
            try:
                return [cell for cell in self.worksheet.range(row, 1, row, self.worksheet.col_count) if cell.col >= min_col]
            except KeyboardInterrupt:
                raise
            except:
                if not retries:
                    logger.warn("Worksheet #%s: error getting row %s.  Out of quota?", self.worksheet.id, row)
                    raise

                delay = retries.pop()
                logger.warn("Worksheet #%s: error getting row %s.  Out of quota?  retrying again in %s seconds!", self.worksheet.id, row, delay)
                time.sleep(delay)

    @cache(key=lambda self, *args, **kwargs: (self.worksheet.id, args, kwargs))
    def get_column(self, col, min_row=2) -> typing.List[gspread.Cell]:
        retries = [305, 135, 35]
        while True:
            try:
                return [cell for cell in self.worksheet.range(1, col, self.worksheet.row_count, col) if cell.row >= min_row]
            except KeyboardInterrupt:
                raise
            except:
                if not retries:
                    logger.warn("Worksheet #%s: error getting column %s.  Out of quota?", self.worksheet.id, col)
                    raise

                delay = retries.pop()
                logger.warn("Worksheet #%s: error getting column %s.  Out of quota?  retrying again in %s seconds!", self.worksheet.id, col, delay)
                time.sleep(delay)

    def set_cells(self, cells):
        if not cells:
            return

        # Sort cells by row and column
        cells = sorted(cells, key=lambda cell: (cell.row, cell.col))

        retries = [305, 135, 35]
        while True:
            try:
                logger.info("Worksheet #%s: persisting %s cells", self.worksheet.id, len(cells))
                return self.worksheet.update_cells(cells)
            except KeyboardInterrupt:
                raise
            except:
                if not retries:
                    logger.warn("Worksheet #%s: error updating %s cells.  Out of quota?", self.worksheet.id, len(cells))
                    raise

                delay = retries.pop()
                logger.warn("Worksheet #%s: error updating %s cells.  Out of quota?  retrying once in %s seconds!", self.worksheet.id, len(cells), delay)
                time.sleep(delay)

    @staticmethod
    def __find_existing_cell(cells: typing.List[gspread.Cell], value: str) -> typing.Optional[gspread.Cell]:
        for cell in cells:
            if cell.value == value:
                return cell

    @staticmethod
    def __create_cell(cells: typing.List[gspread.Cell], value: str, updated_cells: typing.List[gspread.Cell]) -> typing.Optional[gspread.Cell]:
        for cell in cells:
            if cell.value in ("-", "_", "any"):
                cell.value = value
                updated_cells.append(cell)
                return cell

    def find_column_header(self, value: str) -> typing.Optional[gspread.Cell]:
        return self.__find_existing_cell(self.get_row(1), value)

    def find_or_create_column_header(self, value: str, updated_cells: typing.List[gspread.Cell]) -> typing.Optional[gspread.Cell]:
        cells = self.get_row(1)
        cell = self.__find_existing_cell(cells, value)
        if not cell:
            cell = self.__create_cell(cells, value, updated_cells)
        return cell

    def find_row_header(self, value: str) -> typing.Optional[gspread.Cell]:
        return self.__find_existing_cell(self.get_column(1), value)

    def find_or_create_row_header(self, value: str, updated_cells: typing.List[gspread.Cell]) -> typing.Optional[gspread.Cell]:
        cells = self.get_column(1)
        cell = self.__find_existing_cell(cells, value)
        if not cell:
            cell = self.__create_cell(cells, value, updated_cells)
        return cell
