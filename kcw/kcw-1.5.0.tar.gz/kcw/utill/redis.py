from kcw.packages import redis as red
import kcw.config as config
class redis:
    "redis  注意：连接池链接模式下不支持动态配置"
    __redisObj=None
    __config=config.redis
    def __connects(self):
        """设置redis链接"""
        if self.__config['pattern']:
            if not self.__redisObj:
                if self.__config['password']:
                    redis_pool=red.ConnectionPool(host=self.__config['host'],password=self.__config['password'],port=self.__config['port'],db=self.__config['db'])
                else:
                    redis_pool=red.ConnectionPool(host=self.__config['host'],port=self.__config['port'],db=self.__config['db'])
                self.__redisObj=red.Redis(connection_pool=redis_pool)
        else:
            if self.__config['password']:
                self.__redisObj=red.Redis(host=self.__config['host'],password=self.__config['password'],port=self.__config['port'],db=self.__config['db'])
            else:
                self.__redisObj=red.Redis(host=self.__config['host'],port=self.__config['port'],db=self.__config['db'])
            # print(self.__redisObj)
    def getconfig(self):
        return self.__config
    def connect(self,config):
        """设置redis链接信息 

        参数 config 参考配置信息格式

        返回 redis
        """ 
        if config:
            if isinstance(config,dict):
                if "host" in config:
                    self.__config['host']=config['host']
                if "port" in config:
                    self.__config['port']=config['port']
                if "password" in config:
                    self.__config['password']=config['password']
                if "db" in config:
                    self.__config['db']=config['db']
        return self
    def redisObj(self):
        "得到一个redis连接对象，执行更多高级操作"
        self.__connects()
        return self.__redisObj
    def set(self,name,value,ex=None, px=None, nx=False, xx=False):
        """
        name，键

        value，值

        ex，过期时间（秒）

        px，过期时间（毫秒）

        nx，如果设置为True，则只有key不存在时，当前set操作才执行,同#setnx(key, value)

        xx，如果设置为True，则只有key存在时，当前set操作才执行
        """
        if not self.__redisObj:
            self.__connects()
        if not ex and not px:
            if self.__config['ex']:
                ex=self.__config['ex']
        return self.__redisObj.set(name, value, ex=ex, px=px, nx=nx, xx=xx)
    def get(self,name):
        """获取name的值

        name，键
        返回键“name”处的值，如果该键不存在，则返回“none”
        """
        self.__connects()
        return self.__redisObj.get(name)
    def rpush(self,name, *values):
        "元素从list的右边加入"
        self.__connects()
        # print(self.__config)
        return self.__redisObj.rpush(name, *values) 
    def rpop(self,name):
        "元素从list的右边移出"
        self.__connects()
        return self.__redisObj.rpop(name)
    def rpoplpush(self,src, dst):
        "元素从list的右边移出,并且从list的左边加入"
        self.__connects()
        return self.__redisObj.rpoplpush(src, dst)
    def rpushx(self,name, value):
        "当name存在时，元素才能从list的右边加入"
        self.__connects()
        return self.__redisObj.rpushx(name, value)
    def lpush(self,name, *values):
        "元素从list的左边加入，可以添加多个"
        self.__connects()
        return self.__redisObj.lpush(name, *values)
    def lpop(self,name):
        "元素从list的左边移出"
        self.__connects()
        return self.__redisObj.lpop(name)
    def lpushxs(self,name):
        "当name存在时，元素才能从list的左边加入"
        self.__connects()
        return self.__redisObj.lpushx(name)
    def hmset(self,name,mapping,ex=None):
        """在hash“name”中为每个键设置值
        name，键

        mapping，值

        ex,过期时间(秒)
        
        """
        self.__connects()
        boot = self.__redisObj.hmset(name,mapping)

        if not ex:
            if self.__config['ex']:
                ex=self.__config['ex']
        if ex:
            self.__redisObj.expire(name,ex)
        return boot
    def hmget(self,name, keys, *args):
        "返回与“keys”顺序相同的值列表``"
        self.__connects()
        return self.__redisObj.hmget(name, keys, *args)
