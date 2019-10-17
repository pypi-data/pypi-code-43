# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import app
from suanpan import arguments as base  # pylint: disable=unused-import
from suanpan.arguments import auto  # pylint: disable=unused-import
from suanpan.dw import arguments as dw
from suanpan.imports import imports
from suanpan.storage import arguments as storage

Int = imports("suanpan.{}.arguments.Int".format(app.TYPE))
Float = imports("suanpan.{}.arguments.Float".format(app.TYPE))
Bool = imports("suanpan.{}.arguments.Bool".format(app.TYPE))
String = imports("suanpan.{}.arguments.String".format(app.TYPE))
List = imports("suanpan.{}.arguments.List".format(app.TYPE))
ListOfString = imports("suanpan.{}.arguments.ListOfString".format(app.TYPE))
ListOfInt = imports("suanpan.{}.arguments.ListOfInt".format(app.TYPE))
ListOfFloat = imports("suanpan.{}.arguments.ListOfFloat".format(app.TYPE))
ListOfBool = imports("suanpan.{}.arguments.ListOfBool".format(app.TYPE))
IntOrFloat = imports("suanpan.{}.arguments.IntOrFloat".format(app.TYPE))
IntFloatOrString = imports("suanpan.{}.arguments.IntFloatOrString".format(app.TYPE))
BoolOrString = imports("suanpan.{}.arguments.BoolOrString".format(app.TYPE))
StringOrListOfFloat = imports(
    "suanpan.{}.arguments.StringOrListOfFloat".format(app.TYPE)
)
Json = imports("suanpan.{}.arguments.Json".format(app.TYPE))

File = imports("suanpan.{}.arguments.File".format(app.TYPE))
Folder = imports("suanpan.{}.arguments.Folder".format(app.TYPE))
Data = imports("suanpan.{}.arguments.Data".format(app.TYPE))
Csv = imports("suanpan.{}.arguments.Csv".format(app.TYPE))
Npy = imports("suanpan.{}.arguments.Npy".format(app.TYPE))
Visual = imports("suanpan.{}.arguments.Visual".format(app.TYPE))
Model = imports("suanpan.{}.arguments.Model".format(app.TYPE))
H5Model = imports("suanpan.{}.arguments.H5Model".format(app.TYPE))
Checkpoint = imports("suanpan.{}.arguments.Checkpoint".format(app.TYPE))
JsonModel = imports("suanpan.{}.arguments.JsonModel".format(app.TYPE))
Image = imports("suanpan.{}.arguments.Image".format(app.TYPE))

Table = imports("suanpan.{}.arguments.Table".format(app.TYPE))
DataFrame = imports("suanpan.{}.arguments.DataFrame".format(app.TYPE))
