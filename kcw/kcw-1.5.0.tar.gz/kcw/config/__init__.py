# 应用配置
app={}
app['app_name']='' #应用名称
app['app_debug']=True  #是否开启调试模式
app['SECRET_KEY']='reresgrdsafagrewgregrtdge' #session密钥
app['template_folder']='temp'  #设置模板文件目录名 注意：不能配置目录路径 
app['static_folder']='static/' #设置静态url目录名

# 默认数据库配置
database={}
database['type']='mysql' # 数据库类型  目前支持mysql和sqlite
database['host']=['127.0.0.1']#服务器地址 [地址1,地址2,地址3...] 多个地址分布式(主从服务器)下有效
database['port']=[3306] #端口 [端口1,端口2,端口3...]
database['user']=['root']  #用户名 [用户名1,用户名2,用户名3...]
database['password']=['root']  #密码 [密码1,密码2,密码3...]
database['db']=['test']  #数据库名 [数据库名1,数据库名2,数据库名3...]
database['charset']='utf8'   #数据库编码默认采用utf8
database['pattern']=False # True数据库长连接模式 False数据库短连接模式  注：建议web应用使用短连接，cli应用使用长连接
database['cli']=False # 是否以cli方式运行
database['dbObjcount']=1 # 连接池数量（单个数据库地址链接数量），数据库链接实例数量 mysql长链接模式下有效
database['deploy']=0 # 数据库部署方式:0 集中式(单一服务器),1 分布式(主从服务器)  mysql数据库有效
database['master_num']=1 #主服务器数量 不能超过host服务器数量  （等于服务器数量表示读写不分离：主主复制。  小于服务器表示读写分离：主从复制。） mysql数据库有效
database['master_dql']=False #主服务器是否可以执行dql语句 是否可以执行select语句  主服务器数量大于等于host服务器数量时必须设置True
database['break']=0 #断线重连次数，0表示不重连。 注：cli模式下 10秒进行一次重连并且连接次数是当前配置的300倍

#sqlite配置
sqlite={}
sqlite['db']='kcwdb'  # 数据库文件存放地址

#mongodb配置
mongo={}
mongo['host']='127.0.0.1'
mongo['port']='27017'
mongo['user']=''
mongo['password']=''
mongo['db']='test'

# redis配置
redis={}
redis['host']='127.0.0.1' #服务器地址
redis['port']=6379 #端口
redis['password']='fk459915476'  #密码
redis['db']=0 #Redis数据库    注：Redis用0或1或2等表示
redis['pattern']=True # True连接池链接 False非连接池链接
redis['ex']=0  #过期时间 （秒）

#缓存配置
cache={}
cache['type']='File' #驱动方式 支持 File Redis
cache['path']='cachepath/' #缓存保存目录 
cache['expire']=120 #缓存有效期 0表示永久缓存
cache['host']=redis['host'] #Redis服务器地址
cache['port']=redis['port'] #Redis 端口
cache['password']=redis['password'] #Redis登录密码
cache['db']=1 #Redis数据库    注：Redis用1或2或3等表示

#路由配置
route={}
route['default']=True #是否开启默认路由  默认路由开启后面不影响以下配置的路由，文件名和方法名作为路由地址   如：index.py的index方法的默认路由为: /index/index  或/index/index/   #   以下是路由配置
route['defaultparam']=1 #默认路由参数，1表示路由参数中需要参数名   0表示不需要
route['methods']=["POST","GET"] #默认请求方式
# route['/v1/index/test1']={'route':"/test","methods":["GET"]}  #设置view/v1/index.py的test1方法的路由为: /test  并且设置请求方式为GET  配置路由后，该路由的默认路由将不会生效
# route['/v1/login/login']={'route':"/login"}  #设置view/v1/login.py的login方法的路由为: /login 请求方式使用默认


oauth={}
oauth['status']=False   #签权开关
oauth['need']=[	        # “需要” 签权的视图函数
	"*" 	            # *：表示全部。 /index*:表示index视图文件下的所有方法。  /v1*：表示v1下的所有。/v1/index*：表示v1/index下的所有
]
oauth['unwanted']=[
	"login/*"	        #表示login下所有不需要签权
]
#其他配置
other={}


confkcw={}
confkcw['name']='kcw'								#项目的名称
confkcw['version']='1.5.0'							#项目版本
confkcw['description']='一个快速cli和web开发框架,增加sqlitesql驱动，以及mysql和sqlite数据库驱动的字符转义'    #项目的简单描述
confkcw['author']='禄可集团-坤坤'  					 #名字
confkcw['author_email']='fk1402936534@qq.com' 	    #邮件地址
confkcw['maintainer']='坤坤' 						 #维护人员的名字
confkcw['maintainer_email']='fk1402936534@qq.com'    #维护人员的邮件地址
confkcw['url']=''
confkcw['install_requires']=['pymongo==3.9.0','six==1.12.0','requests==2.22.0'] #第三方包