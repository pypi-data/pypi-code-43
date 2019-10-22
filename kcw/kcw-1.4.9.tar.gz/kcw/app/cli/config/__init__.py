from config import *
# 默认数据库配置
database['pattern']=True # True数据库长连接模式 False数据库短连接模式  注：建议web应用使用短连接，cli应用使用长连接
database['cli']=True # 是否以cli方式运行
database['dbObjcount']=1 # 连接池数量（单个数据库地址链接数量），数据库链接实例数量 mysql长链接模式下有效



