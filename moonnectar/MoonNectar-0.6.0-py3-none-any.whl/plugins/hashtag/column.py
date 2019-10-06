import Registry.Library.Columns

from mnectar.library.column import Column

class HashtagColumn(Registry.Plugin, registry=Registry.Library.Columns):
    def enable(self):
        self.app.columns.add(
            Column(
                "hashtag",
                "Hashtags",
                200,
                displayFunc = lambda r,c: ", ".join(sorted(r[c])),
                sortFunc    = lambda r,c: ",".join(sorted(r[c])).lower(),
                sortDefault = [],
                hidden      = True,
            )
        )
