from config import *
app['app_name']=''                                  #应用名称
app['app_debug']=True                               #是否开启调试模式
app['SECRET_KEY']='reresgrdsafagrewgregrtdge'       #session密钥
app['template_folder']='temp'                       ##设置模板文件目录名 注意：不能配置目录路径 

#签权/登录配置
oauth['status']=True    #签权开关
oauth['need']=[	        # “需要” 签权的视图函数
	"*" 	        # *：表示全部。 /index*:表示index视图文件下的所有方法。  /v1*：表示v1下的所有。/v1/index*：表示v1/index下的所有
]
oauth['unwanted']=[		# “不需要” 签权的视图函数
	"index/*",	        #表示login下所有不需要签权
	"/"
]

route['defaultparam']=0    #设置路由中的参数名在url上不需要显示
route['/index/index']=[{'route':"/<html>","methods":["GET"]},{'route':"/","methods":["GET"]}]


