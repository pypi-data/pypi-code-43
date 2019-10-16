# https://stackoverflow.com/questions/21503865/how-to-denote-that-a-command-line-argument-is-optional-when-printing-usage
# TODO improve help information

TOP_MESSAGE = "Press `F1` to show help."


HELP_TEXT = """

coderadio
---------

Press `Ctrl + Up` or `Ctrl + Down` to move the focus.
Press `UP` or `Down` to navigate between stations
To exit press `Ctrl + q` or type `exit` in the prompt and press enter.


Command List
------------

Player commands
---------------

play byid <id>
stop


Search commands
---------------

list bycodec <codec>
list bycodecexact <codecexact>
list bycountry <country>
list bycountryexact <countryexact>
list byid <id>
list bylanguage <language>
list bylanguageexact <languageexact>
list byname <name>
list bynameexact <nameexact>
list bystate <state>
list bystateexact <stateexact>
list bytag <tag>
list bytagexact <tag>
list byuuid <uuid>
list tags

Help commands
--------------

help 

To close this window, change focus with `Ctrl + Up` or `Ctrl + Down`.

"""
