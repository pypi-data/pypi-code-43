from kcw.packages.flask import Blueprint
from config import app
app = Blueprint(
   'application',
   __name__,
   static_folder="../"+app['static_folder'],#设置静态url目录
   template_folder="../"+app['template_folder'],#设置模板文件目录
)
from . import index,login #z这里导入您的视图文件 如：from . import index,index1,index2...
from .v1 import index #z这里导入您的视图文件 如：from .v1 import index,index1,index2...
from .v2 import index #z这里导入您的视图文件 如：from .v2 import index,index1,index2...

