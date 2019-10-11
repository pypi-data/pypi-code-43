#
# Schematic API constants.
#
#
# This file is a part of Typhoon HIL API library.
#
# Typhoon HIL API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import print_function, unicode_literals

# Icon rotate behavior constants.
ICON_ROTATE = "rotate"
ICON_NO_ROTATE = "no_rotate"
ICON_TEXT_LIKE = "text_like"

# Fully qualified name separator
FQN_SEP = "."

# Signal processing type constants.
SP_TYPE_INHERIT = "inherit"
SP_TYPE_INT = "int"
SP_TYPE_UINT = "uint"
SP_TYPE_REAL = "real"

# Kind constants.
KIND_SP = "sp"
KIND_PE = "pe"

# Direction constants.
DIRECTION_IN = "in"
DIRECTION_OUT = "out"

# Constants for specifying rotation.
ROTATION_DOWN = "down"
ROTATION_UP = "up"
ROTATION_LEFT = "left"
ROTATION_RIGHT = "right"

# Constants for specifying tag scopes.
TAG_SCOPE_LOCAL = "local"
TAG_SCOPE_GLOBAL = "global"
TAG_SCOPE_MASKED_SUBSYSTEM = "masked_subsystem"

# Constant for ItemHandle type
ITEM_HANDLE = "item_handle"

# Flip constants.
FLIP_NONE = "flip_none"
FLIP_HORIZONTAL = "flip_horizontal"
FLIP_VERTICAL = "flip_vertical"
FLIP_BOTH = "flip_both"

# Constants used for specifying item types.
ITEM_ANY = "unknown"
ITEM_COMPONENT = "component"
ITEM_MASKED_COMPONENT = "masked_component"
ITEM_MASK = "mask"
ITEM_CONNECTION = "connection"
ITEM_TAG = "tag"
ITEM_PORT = "port"
ITEM_COMMENT = "comment"
ITEM_JUNCTION = "junction"
ITEM_TERMINAL = "terminal"
ITEM_PROPERTY = "property"

# Constants used for specifying kind of error and/or warning.
ERROR_GENERAL = "General error"
ERROR_PROPERTY_VALUE_INVALID = "Invalid property value"

WARNING_GENERAL = "General warning"

# Constants used for specifying simulation method.
SIM_METHOD_EXACT = "exact"
SIM_METHOD_EULER = "euler"
SIM_METHOD_TRAPEZOIDAL = "trapezoidal"

GRID_RESOLUTION = 8

# Constants for handler names.
HANDLER_MASK_INIT = "mask_init"
HANDLER_MASK_PRE_COMPILE = "mask_pre_cmpl"
HANDLER_PROPERTY_VALUE_CHANGED = "property_value_changed"
HANDLER_PROPERTY_VALUE_EDITED = "property_value_edited"

# Constants for specifying widget types.
WIDGET_COMBO = "combo"
WIDGET_EDIT = "edit"
WIDGET_CHECKBOX = "checkbox"
WIDGET_BUTTON = "button"
