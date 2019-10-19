# cqldbdelete.py
# Copyright 2016 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Delete dialogue for Chess Query Language (ChessQL) statement record.
"""

from solentware_grid.gui.datadelete import DataDelete

from .chessexception import ChessException
from .cqldisplay import DialogueCQLDisplay


class ChessDBdeleteCQL(ChessException, DataDelete):
    """Dialog to delete a ChessQL statement from database.

    The ChessQL statement is in it's own Toplevel widget.

    """

    def __init__(self, parent, instance, ui=None):
        """Extend and create dialogue widget for deleting ChessQL statement."""
        oldview = DialogueCQLDisplay(master=parent, ui=ui)
        if ui is not None:
            ui.partials_in_toplevels.add(oldview)
        oldview.cql_statement.process_cql_statement(instance.get_srvalue())
        oldview.set_cql_statement(instance.value)
        super().__init__(
            instance,
            parent,
            oldview,
            ':  '.join((
                'Delete ChessQL statement',
                instance.value.get_name_text())),
            )
        self.bind_buttons_to_widget(oldview.score)
        self.ui = ui
       
    def dialog_ok(self):
        """Delete record and return delete action response (True for deleted).

        Check that database is open and is same one as deletion action was
        started.

        """
        if self.ui.database is None:
            self.status.configure(
                text='Cannot delete because not connected to a database')
            if self.ok:
                self.ok.destroy()
                self.ok = None
            self.blockchange = True
            return False
        return super().dialog_ok()

    def tidy_on_destroy(self):
        """Clear up after dialogue destruction."""
        self.ui.partials_in_toplevels.discard(self.oldview)
        self.ui.base_partials.selection.clear()

    def delete(self, commit=True):
        """Delete the record and refresh widgets.

        The ChessQL query statement update is delegated to the superclass.

        This method deletes the foundset calculated from the query.

        """
        if commit:
            self.datasource.dbhome.start_transaction()
        super().delete(commit=False)
        cqls = self.ui.partialpositionds(
            self.ui.base_games.datasource.dbhome,
            self.ui.base_games.datasource.dbset,
            self.ui.base_games.datasource.dbset,
            newrow=None)
        cqls.forget_cql_statement_games(self.object, commit=False)
        if commit:
            self.datasource.dbhome.commit()
