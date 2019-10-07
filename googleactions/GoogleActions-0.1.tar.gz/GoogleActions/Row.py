from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .Cell import Cell


class Row(MyDict):
    """
    {
      "cells": [
        {
          object(Cell)
        }
      ],
      "dividerAfter": boolean
    }
    """

    cells: List[Cell] = DictProperty('cells', list)
    divider_after: bool = DictProperty('dividerAfter', bool)

    def build(self, divider_after:bool=False, *cells:Cell):
        self.divider_after = divider_after
        self.cells = cells
        return self

    def add_cells(self, *cells: Cell) -> List[Cell]:
        for item in cells:
            assert isinstance(item, Cell)
            self.cells.append(item)

        return self.cells

    def add_cell(self, text:str) -> Cell:
        cell = Cell().build(text=text)
        self.cells.append(cell)

        return cell
