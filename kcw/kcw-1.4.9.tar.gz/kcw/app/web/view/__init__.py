from kcw.packages.flask import Blueprint
app = Blueprint('application',__name__)
#以上代码不能修改


#导入视图文件
from . import index
from .v1 import index
from .v2 import index
