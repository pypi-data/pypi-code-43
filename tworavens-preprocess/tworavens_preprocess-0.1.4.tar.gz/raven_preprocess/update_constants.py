"""Constants related to update metadata requests
Will be switched to a JSON schema check

Example update request:
 {
    "preprocessId": 5,
    "variableUpdates": {
       "cylinders" : {
         "viewable": true,
         "omit": ["mean", "median"],
         "valueUpdates": {
             "numchar":"character",
             "nature": "ordinal"
         }
       },
       "mpg": {
         "viewable": false,
         "omit": [],
         "valueUpdates": {

         }
       }
    }
}
"""

VARIABLE_UPDATES = 'variableUpdates'

VIEWABLE_KEY = 'viewable'
OMIT_KEY = 'omit'
VALUE_UPDATES_KEY = 'valueUpdates'

# ----------------
START_ROW = 'startRow'
NUM_ROWS = 'numberRows'
